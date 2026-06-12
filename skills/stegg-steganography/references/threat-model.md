# threat model notes for stegg

Read this file before using steganography for users facing state repression, cartel violence, organized crime retaliation, or other adversaries with device seizure, traffic monitoring, or content inspection capabilities.

## What steganography is good for

- Concealing that a file contains an embedded payload at all
- Smuggling a small ciphertext blob inside an innocuous-looking image
- Reducing attention on a transfer when the adversary is doing shallow inspection

## What steganography does not solve

- Endpoint compromise
- Malware on the sending or receiving device
- A coerced unlock or forensic seizure of the device holding plaintext
- Protection of the payload if the payload itself is not encrypted
- Safe delivery through platforms that resize, recompress, or strip files

## Safer operating pattern

1. Create the sensitive content locally.
2. Encrypt it first with a separate tool and store the ciphertext as a file.
3. Embed the ciphertext file in a fresh PNG carrier with `uvx stegg encode-cmd`.
4. Verify decode locally before sending anything onward.
5. Send only through a path that preserves the file byte-for-byte.
6. Keep plaintext and stego outputs compartmentalized.

## Transfer channels to avoid

- Social media uploads
- Messaging platforms that resize or recompress images
- CMS pipelines that convert PNG to JPEG or WebP
- Any workflow that adds watermarks or strips metadata unpredictably

## Operational mistakes that matter

- Putting the real secret directly in a shell argument instead of a file
- Reusing the same carrier repeatedly for multiple sensitive payloads
- Forgetting to verify the round trip before the original plaintext is moved or deleted
- Treating built-in stego passwords as a substitute for independent encryption
- Assuming concealment still helps after the device or workstation is already compromised
