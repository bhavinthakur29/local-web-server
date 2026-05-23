import http.server
import socketserver
import sys
import os
import html
import http.cookies
import json
import hashlib
import time
import gzip
import io
import threading
import urllib.parse
from datetime import datetime

PASSCODE_HASH = None
REQUEST_LOG   = []
MAX_LOG       = 500
LOG_LOCK      = threading.Lock()
SERVER_START  = time.time()

COMPRESSIBLE = {
    "text/html", "text/css", "text/plain", "text/javascript",
    "application/javascript", "application/json", "image/svg+xml",
}


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads      = True


class ProtectedHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # ── Fix 1: no reverse-DNS (biggest latency killer on LAN) ────────
    def address_string(self):
        return self.client_address[0]

    # ── Request log ───────────────────────────────────────────────────
    def log_message(self, format, *args):
        with LOG_LOCK:
            REQUEST_LOG.append({
                "time":   datetime.now().strftime("%H:%M:%S"),
                "method": self.command or "?",
                "path":   self.path.split("?")[0] if self.path else "/",
                "status": args[1] if len(args) > 1 else "?",
            })
            if len(REQUEST_LOG) > MAX_LOG:
                REQUEST_LOG.pop(0)

    # ── Auth ──────────────────────────────────────────────────────────
    def _get_cookie_token(self):
        cookies = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
        return cookies["auth_token"].value if "auth_token" in cookies else None

    def _token_matches(self, token):
        if not token or not PASSCODE_HASH:
            return False
        if token == PASSCODE_HASH:
            return True
        return hashlib.sha256(token.encode()).hexdigest() == PASSCODE_HASH

    def _is_authorized(self):
        if not PASSCODE_HASH:
            return True
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        raw = params.get("passcode", [""])[0].strip()
        if raw and hashlib.sha256(raw.encode()).hexdigest() == PASSCODE_HASH:
            self.auth_success_token = PASSCODE_HASH
            return True
        token = self._get_cookie_token()
        if self._token_matches(token):
            return True
        return False

    # ── Dispatch ──────────────────────────────────────────────────────
    def do_GET(self):
        if self.path.split("?")[0] == "/__status__":
            self._serve_status()
            return
        if self._is_authorized():
            self.auth_success = True
            super().do_GET()
        else:
            self._send_403()

    def do_HEAD(self):
        if self._is_authorized():
            self.auth_success = True
            super().do_HEAD()
        else:
            self._send_403()

    def _send_403(self):
        accept = self.headers.get("Accept", "")
        if "text/html" in accept:
            body = _LOGIN_PAGE.encode("utf-8")
            content_type = "text/html; charset=utf-8"
        else:
            body = b"Access Denied: Invalid Passcode"
            content_type = "text/plain"
        self.send_response(403)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    # ── Status endpoint ───────────────────────────────────────────────
    def _serve_status(self):
        with LOG_LOCK:
            payload = json.dumps({
                "status":   "running",
                "uptime":   round(time.time() - SERVER_START),
                "requests": len(REQUEST_LOG),
                "log":      list(REQUEST_LOG[-20:]),
            }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    # ── Fix 2: proper gzip directory listing ─────────────────────────
    # We take full ownership of the response here (headers + body)
    # and return None so do_GET / copyfile are never called afterward.
    def list_directory(self, path):
        try:
            entries = os.listdir(path)
        except OSError:
            self.send_error(404, "Cannot list directory")
            return None

        entries.sort(key=str.lower)

        display_path = html.escape(urllib.parse.unquote(self.path, errors="surrogatepass"))
        title = f"Index of {display_path}"

        rows = []
        if display_path != "/":
            rows.append('<tr><td><a href="../">../</a></td><td>—</td><td>—</td></tr>')

        for name in entries:
            fullname = os.path.join(path, name)
            is_dir   = os.path.isdir(fullname)
            is_link  = os.path.islink(fullname)
            display  = html.escape(name + ("/" if is_dir else ("@" if is_link else "")))
            link     = urllib.parse.quote(name + ("/" if is_dir else ""), errors="surrogatepass")
            try:
                stat  = os.stat(fullname)
                size  = "—" if is_dir else _fmt_size(stat.st_size)
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            except OSError:
                size = mtime = "—"
            rows.append(
                f'<tr><td><a href="{link}">{display}</a></td>'
                f'<td>{mtime}</td><td style="text-align:right">{size}</td></tr>'
            )

        raw = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
       background:#0f1117;color:#e2e8f0;padding:24px 16px;max-width:860px;margin:auto}}
  h1{{font-size:1.1rem;font-weight:600;color:#94a3b8;margin-bottom:20px;word-break:break-all}}
  table{{width:100%;border-collapse:collapse;font-size:.9rem}}
  th{{text-align:left;color:#64748b;font-weight:500;font-size:.75rem;
      letter-spacing:.05em;text-transform:uppercase;
      padding:6px 10px;border-bottom:1px solid #1e2333}}
  td{{padding:8px 10px;border-bottom:1px solid #1a1d27;white-space:nowrap}}
  td:first-child{{white-space:normal;word-break:break-all;width:60%}}
  td:last-child{{text-align:right}}
  a{{color:#4f8ef7;text-decoration:none}}a:hover{{text-decoration:underline}}
  tr:hover td{{background:#1a1d27}}
</style></head>
<body><h1>{title}</h1>
<table><thead><tr><th>Name</th><th>Modified</th><th>Size</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
</body></html>""".encode("utf-8", "surrogateescape")

        accept = self.headers.get("Accept-Encoding", "")
        use_gz = "gzip" in accept
        if use_gz:
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=6) as gz:
                gz.write(raw)
            body = buf.getvalue()
        else:
            body = raw

        # Send everything ourselves — do NOT call end_headers() here
        # because end_headers() is invoked by send_response → we use
        # send_response + send_header + end_headers manually.
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if use_gz:
            self.send_header("Content-Encoding", "gzip")
        # end_headers() calls our override which adds Cookie/Cache headers
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)
        # Return None so SimpleHTTPRequestHandler.do_GET does NOT
        # try to call copyfile() on our response.
        return None

    # ── Cookie + cache headers ────────────────────────────────────────
    def end_headers(self):
        token = getattr(self, "auth_success_token", None)
        if token:
            cookie = http.cookies.SimpleCookie()
            cookie["auth_token"] = token
            cookie["auth_token"]["path"] = "/"
            cookie["auth_token"]["max-age"] = 3600
            cookie["auth_token"]["httponly"] = True
            cookie["auth_token"]["samesite"] = "Strict"
            value = cookie.output(header="").strip()
            if value:
                self.send_header("Set-Cookie", value)
        if getattr(self, "auth_success", False):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    # ── Extra MIME types ──────────────────────────────────────────────
    def guess_type(self, path):
        ext = os.path.splitext(path)[1].lower()
        return {
            ".avif": "image/avif",
            ".webp": "image/webp",
            ".woff2": "font/woff2",
            ".woff": "font/woff",
        }.get(ext, super().guess_type(path))


_LOGIN_PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Access Required</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
       background:#0f1117;color:#e2e8f0;min-height:100vh;display:flex;
       align-items:center;justify-content:center;padding:24px}
  .card{background:#1a1d27;border:1px solid #2a2d3a;border-radius:12px;
        padding:28px;width:100%;max-width:360px}
  h1{font-size:1.1rem;margin-bottom:8px}
  p{color:#94a3b8;font-size:.9rem;margin-bottom:20px}
  label{display:block;font-size:.75rem;color:#64748b;margin-bottom:6px}
  input{width:100%;padding:10px 12px;border-radius:6px;border:1px solid #2a2d3a;
        background:#0f1117;color:#e2e8f0;font-size:1rem}
  button{margin-top:16px;width:100%;padding:10px;border:none;border-radius:6px;
         background:#4f8ef7;color:#fff;font-size:.95rem;font-weight:600;cursor:pointer}
  button:hover{background:#3b7de8}
</style></head>
<body><div class="card">
<h1>Access Required</h1>
<p>Enter the passcode from TekServe Local to browse this folder.</p>
<form method="GET" action="/">
<label for="passcode">Passcode</label>
<input id="passcode" name="passcode" type="password" autocomplete="current-password" required autofocus>
<button type="submit">Continue</button>
</form></div></body></html>"""


def _fmt_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def run_server(port, directory, passcode=""):
    global PASSCODE_HASH
    PASSCODE_HASH = hashlib.sha256(passcode.encode()).hexdigest() if passcode else None
    os.chdir(directory)
    with ThreadedTCPServer(("", port), ProtectedHandler) as httpd:
        print(f"RUNNING:{port}", flush=True)
        httpd.serve_forever()


def main(argv=None):
    argv = list(argv) if argv is not None else sys.argv[1:]
    try:
        if len(argv) < 2:
            raise ValueError("usage: server_core <port> <directory> [passcode]")
        port = int(argv[0])
        directory = argv[1]
        passcode = argv[2] if len(argv) > 2 else ""
        run_server(port, directory, passcode)
    except Exception as e:
        print(f"ERROR:{e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()