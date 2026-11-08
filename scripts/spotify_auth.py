"""One-time helper: get a Spotify refresh token for the Now Playing card.

1. Create an app at https://developer.spotify.com/dashboard
   - Redirect URI:  http://127.0.0.1:8888/callback
   - API: Web API
2. Run:  python scripts/spotify_auth.py <CLIENT_ID> <CLIENT_SECRET>
3. Log in to Spotify in the browser window that opens and click Agree.
4. Copy the three values it prints into the repo's
   Settings > Secrets and variables > Actions > New repository secret.

Nothing is saved to disk; the token is only printed in this terminal.
"""
import base64
import http.server
import json
import secrets
import sys
import urllib.parse
import urllib.request
import webbrowser

REDIRECT = "http://127.0.0.1:8888/callback"
SCOPES = "user-read-currently-playing user-read-recently-played"


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    cid, secret = sys.argv[1], sys.argv[2]
    state = secrets.token_urlsafe(16)
    result = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            ok = q.get("state", [None])[0] == state and "code" in q
            if ok:
                result["code"] = q["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            msg = "Done! You can close this tab." if ok else "Authorization failed. Check the terminal."
            self.wfile.write(f"<h2 style='font-family:sans-serif'>{msg}</h2>".encode())

        def log_message(self, *a):
            pass

    url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(
        {"client_id": cid, "response_type": "code", "redirect_uri": REDIRECT, "scope": SCOPES, "state": state})
    print("Opening browser for Spotify login...\nIf it doesn't open, visit:\n" + url)
    webbrowser.open(url)
    with http.server.HTTPServer(("127.0.0.1", 8888), Handler) as srv:
        while "code" not in result:
            srv.handle_request()

    auth = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=urllib.parse.urlencode({"grant_type": "authorization_code", "code": result["code"],
                                     "redirect_uri": REDIRECT}).encode(),
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as r:
        tok = json.load(r)

    print("\nAdd these as repository secrets on github.com/DMVDXN/DMVDXN:\n")
    print(f"  SPOTIFY_CLIENT_ID      = {cid}")
    print(f"  SPOTIFY_CLIENT_SECRET  = {secret}")
    print(f"  SPOTIFY_REFRESH_TOKEN  = {tok['refresh_token']}")


if __name__ == "__main__":
    main()
