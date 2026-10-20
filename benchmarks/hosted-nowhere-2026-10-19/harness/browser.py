"""Generic browser client. No app-specific selectors or task answers.

Usage: python3 browser.py goto URL | snapshot | fill SELECTOR VALUE |
       click SELECTOR | select SELECTOR VALUE | screenshot OUTPUT.png
"""
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
    print(__doc__)
    raise SystemExit(0)

action, *args = sys.argv[1:]
request = Request(os.environ['E2E_SERVICES_URL'] + '/browser',
                  data=json.dumps({'action': action, 'args': args}).encode(),
                  headers={'Content-Type': 'application/json'})
try:
    with urlopen(request, timeout=90) as response:
        print(response.read().decode())
except HTTPError as error:
    print(error.read().decode())
    raise SystemExit(1)
