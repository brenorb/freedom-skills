"""Minimal local Blossom server for blossom-cli end-to-end tests.

Implements the parts of BUD-01, BUD-02 and BUD-04 that the blossom-cli skill
exercises, and verifies kind 24242 authorization events (event id and BIP-340
Schnorr signature, `t` tag, `x` tag, expiration). Uses only the standard
library so the tests can run anywhere `uvx` can.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from urllib.request import urlopen

# --- BIP-340 Schnorr verification (reference algorithm) -------------------

_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)


def _tagged_hash(tag: str, msg: bytes) -> bytes:
    tag_hash = hashlib.sha256(tag.encode()).digest()
    return hashlib.sha256(tag_hash + tag_hash + msg).digest()


def _point_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    if p1[0] == p2[0] and p1[1] != p2[1]:
        return None
    if p1 == p2:
        lam = (3 * p1[0] * p1[0] * pow(2 * p1[1], _P - 2, _P)) % _P
    else:
        lam = ((p2[1] - p1[1]) * pow(p2[0] - p1[0], _P - 2, _P)) % _P
    x3 = (lam * lam - p1[0] - p2[0]) % _P
    return (x3, (lam * (p1[0] - x3) - p1[1]) % _P)


def _point_mul(point, scalar: int):
    result = None
    for i in range(256):
        if (scalar >> i) & 1:
            result = _point_add(result, point)
        point = _point_add(point, point)
    return result


def _lift_x(x: int):
    if x >= _P:
        return None
    y_sq = (pow(x, 3, _P) + 7) % _P
    y = pow(y_sq, (_P + 1) // 4, _P)
    if pow(y, 2, _P) != y_sq:
        return None
    return (x, y if y % 2 == 0 else _P - y)


def schnorr_verify(msg: bytes, pubkey: bytes, sig: bytes) -> bool:
    if len(pubkey) != 32 or len(sig) != 64:
        return False
    point = _lift_x(int.from_bytes(pubkey, "big"))
    r = int.from_bytes(sig[:32], "big")
    s = int.from_bytes(sig[32:], "big")
    if point is None or r >= _P or s >= _N:
        return False
    e = int.from_bytes(_tagged_hash("BIP0340/challenge", sig[:32] + pubkey + msg), "big") % _N
    result = _point_add(_point_mul(_G, s), _point_mul(point, _N - e))
    return result is not None and result[1] % 2 == 0 and result[0] == r


# --- Nostr authorization -------------------------------------------------


class AuthError(Exception):
    def __init__(self, message: str, event: dict | None = None) -> None:
        super().__init__(message)
        self.event = event


def event_id(event: dict) -> str:
    serialized = json.dumps(
        [0, event["pubkey"], event["created_at"], event["kind"], event["tags"], event["content"]],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(serialized.encode()).hexdigest()


def verify_auth(header: str | None, action: str, sha256: str | None) -> dict:
    if not header or not header.startswith("Nostr "):
        raise AuthError("missing Nostr authorization")
    token = header[len("Nostr ") :].strip()
    token += "=" * (-len(token) % 4)  # clients commonly send unpadded base64
    try:
        decode = base64.urlsafe_b64decode if ("-" in token or "_" in token) else base64.b64decode
        event = json.loads(decode(token))
    except (ValueError, json.JSONDecodeError) as exc:
        raise AuthError(f"malformed authorization: {exc}") from exc
    if event.get("kind") != 24242:
        raise AuthError("authorization event must be kind 24242", event)
    if event_id(event) != event.get("id"):
        raise AuthError("authorization event id mismatch", event)
    if not schnorr_verify(bytes.fromhex(event["id"]), bytes.fromhex(event["pubkey"]), bytes.fromhex(event["sig"])):
        raise AuthError("invalid authorization signature", event)
    tags = event.get("tags", [])
    if ["t", action] not in [tag[:2] for tag in tags]:
        raise AuthError(f"authorization is not scoped to {action!r}", event)
    expirations = [int(tag[1]) for tag in tags if tag[:1] == ["expiration"]]
    if not expirations or min(expirations) <= time.time():
        raise AuthError("authorization is missing or past its expiration", event)
    if sha256 is not None:
        hashes = [tag[1] for tag in tags if tag[:1] == ["x"]]
        if sha256 not in hashes:
            raise AuthError("authorization is not scoped to this blob hash", event)
    return event


# --- Server ----------------------------------------------------------------

HASH_PATH = re.compile(r"^/([0-9a-f]{64})(\.[A-Za-z0-9]+)?$")


@dataclass
class Blob:
    data: bytes
    content_type: str
    uploaded: int
    owners: set[str] = field(default_factory=set)


@dataclass
class Request:
    method: str
    path: str
    status: int
    auth: dict | None


class BlossomTestServer:
    """In-memory Blossom server.

    `faults` maps (METHOD, path-prefix) to an injected status code.
    `require_x_tags` enforces BUD-11's matching `x` tag on delete and mirror;
    disable it to emulate servers that accept unscoped authorization.
    """

    def __init__(self) -> None:
        self.require_x_tags = True
        self.blobs: dict[str, Blob] = {}
        self.faults: dict[tuple[str, str], int] = {}
        self.requests: list[Request] = []
        self._lock = threading.Lock()
        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        host, port = self._httpd.server_address[:2]
        return f"http://{host}:{port}"

    def __enter__(self) -> "BlossomTestServer":
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()

    def descriptor(self, sha256: str) -> dict:
        blob = self.blobs[sha256]
        return {
            "url": f"{self.url}/{sha256}",
            "sha256": sha256,
            "size": len(blob.data),
            "type": blob.content_type,
            "uploaded": blob.uploaded,
        }

    def _store(self, data: bytes, content_type: str, owner: str) -> str:
        sha256 = hashlib.sha256(data).hexdigest()
        with self._lock:
            blob = self.blobs.setdefault(sha256, Blob(data, content_type, int(time.time())))
            blob.owners.add(owner)
        return sha256

    def _handler(self):
        server = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args) -> None:  # keep pytest output clean
                pass

            def _send(self, status: int, body: bytes = b"", content_type: str = "application/json",
                      auth: dict | None = None, reason: str | None = None) -> None:
                auth = auth or getattr(self, "rejected_auth", None)
                server.requests.append(Request(self.command, self.path, status, auth))
                self.send_response(status)
                self.send_header("Access-Control-Allow-Origin", "*")
                if reason:
                    self.send_header("X-Reason", reason)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(body)

            def _json(self, status: int, payload, auth: dict | None = None) -> None:
                self._send(status, json.dumps(payload).encode(), auth=auth)

            def _error(self, status: int, message: str) -> None:
                self._send(status, json.dumps({"message": message}).encode(), reason=message)

            def _body(self) -> bytes:
                length = int(self.headers.get("Content-Length") or 0)
                return self.rfile.read(length) if length else b""

            def _fault(self) -> bool:
                path = urlparse(self.path).path
                for (method, prefix), status in server.faults.items():
                    if method == self.command and path.startswith(prefix):
                        self._body()
                        self._error(status, "injected fault")
                        return True
                return False

            def do_HEAD(self) -> None:
                self.do_GET()

            def do_GET(self) -> None:
                if self._fault():
                    return
                path = urlparse(self.path).path
                if path in ("/", "/status", "/health"):
                    self._json(200, {"status": "ok", "blobs": len(server.blobs)})
                    return
                if path.startswith("/list/"):
                    pubkey = path[len("/list/") :]
                    items = [server.descriptor(h) for h, b in server.blobs.items() if pubkey in b.owners]
                    self._json(200, items)
                    return
                match = HASH_PATH.match(path)
                if not match:
                    self._error(404, "not found")
                    return
                blob = server.blobs.get(match.group(1))
                if blob is None:
                    self._error(404, "blob not found")
                    return
                self._send(200, blob.data, content_type=blob.content_type)

            def do_PUT(self) -> None:
                if self._fault():
                    return
                path = urlparse(self.path).path
                body = self._body()
                if path == "/upload":
                    sha256 = hashlib.sha256(body).hexdigest()
                    try:
                        event = verify_auth(self.headers.get("Authorization"), "upload", sha256)
                    except AuthError as exc:
                        self.rejected_auth = exc.event
                        self._error(401, str(exc))
                        return
                    content_type = self.headers.get("Content-Type") or "application/octet-stream"
                    server._store(body, content_type, event["pubkey"])
                    self._json(200, server.descriptor(sha256), auth=event)
                    return
                if path == "/mirror":
                    try:
                        source = json.loads(body)["url"]
                    except (ValueError, KeyError):
                        self._error(400, "mirror body must be JSON with a url")
                        return
                    claimed = re.findall(r"[0-9a-f]{64}", urlparse(source).path)
                    try:
                        event = verify_auth(
                            self.headers.get("Authorization"),
                            "upload",
                            (claimed[-1] if claimed else "") if server.require_x_tags else None,
                        )
                    except AuthError as exc:
                        self.rejected_auth = exc.event
                        self._error(401, str(exc))
                        return
                    try:
                        with urlopen(source, timeout=10) as response:
                            data = response.read()
                            content_type = response.headers.get("Content-Type") or "application/octet-stream"
                    except OSError as exc:
                        self._error(502, f"could not fetch mirror source: {exc}")
                        return
                    sha256 = hashlib.sha256(data).hexdigest()
                    if claimed and claimed[-1] != sha256:
                        self._error(409, "mirrored bytes do not match source hash")
                        return
                    server._store(data, content_type, event["pubkey"])
                    self._json(200, server.descriptor(sha256), auth=event)
                    return
                self._error(404, "not found")

            def do_DELETE(self) -> None:
                if self._fault():
                    return
                match = HASH_PATH.match(urlparse(self.path).path)
                if not match:
                    self._error(404, "not found")
                    return
                sha256 = match.group(1)
                try:
                    event = verify_auth(
                        self.headers.get("Authorization"), "delete", sha256 if server.require_x_tags else None
                    )
                except AuthError as exc:
                    self.rejected_auth = exc.event
                    self._error(401, str(exc))
                    return
                blob = server.blobs.get(sha256)
                if blob is None:
                    self._error(404, "blob not found")
                    return
                if event["pubkey"] not in blob.owners:
                    self._error(403, "not an owner of this blob")
                    return
                with server._lock:
                    blob.owners.discard(event["pubkey"])
                    if not blob.owners:
                        del server.blobs[sha256]
                self._json(200, {"deleted": sha256}, auth=event)

        return Handler
