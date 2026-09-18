#!/usr/bin/env python3
"""Local writing workbench. Serves one page and a small JSON API over the repo files.
Stdlib only. Never writes outside content/ (via bin scripts) and coach/ (via claude)."""
import json, os, re, subprocess, sys, webbrowser
from datetime import date
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "content", "posts")
PORT = int(os.environ.get("WB_PORT", "8787"))
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

def run(cmd, timeout=60, env=None):
    e = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    if env: e.update(env)
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout, env=e)
    return p.returncode, (p.stdout + p.stderr).strip()

def split_fm(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m: return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.startswith(" "): continue
        k, v = line.split(":", 1); v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'": v = v[1:-1]
        fm[k.strip()] = v
    return fm, m.group(2)

def join_fm(fm, body):
    order = ["title", "date", "version", "draft", "changes"]
    lines = []
    for k in order + [k for k in fm if k not in order]:
        if k not in fm: continue
        v = fm[k]
        if k in ("title", "changes"): v = json.dumps(str(v), ensure_ascii=False)
        lines.append(f"{k}: {v}")
    return "---\n" + "\n".join(lines) + "\n---\n" + body.rstrip("\n") + "\n"

def piece_dir(slug):
    if not SLUG_RE.match(slug): raise ValueError("bad slug")
    d = os.path.join(POSTS, slug)
    if not os.path.isdir(d): raise FileNotFoundError(slug)
    return d

def version_path(slug, n):
    n = int(n)
    p = os.path.join(piece_dir(slug), f"v{n}.md")
    if not os.path.isfile(p): raise FileNotFoundError(f"v{n}")
    return p

def list_pieces():
    out = []
    if not os.path.isdir(POSTS): return out
    for slug in sorted(os.listdir(POSTS)):
        d = os.path.join(POSTS, slug)
        idx = os.path.join(d, "_index.md")
        if not os.path.isdir(d) or not os.path.isfile(idx): continue
        fm, _ = split_fm(open(idx, encoding="utf-8").read())
        versions = []
        for f in os.listdir(d):
            m = re.match(r"^v(\d+)\.md$", f)
            if not m: continue
            vfm, body = split_fm(open(os.path.join(d, f), encoding="utf-8").read())
            versions.append({"n": int(m.group(1)), "draft": vfm.get("draft", "true") == "true",
                             "date": vfm.get("date", ""), "words": len(body.split()),
                             "changes": vfm.get("changes", "")})
        versions.sort(key=lambda v: v["n"])
        out.append({"slug": slug, "title": fm.get("title", slug), "draft": fm.get("draft", "true") == "true",
                    "date": fm.get("date", ""), "versions": versions})
    out.sort(key=lambda p: p["date"], reverse=True)
    return out

def coach_log(slug):
    p = os.path.join(ROOT, "coach", "log", f"{slug}.md")
    return open(p, encoding="utf-8").read() if os.path.isfile(p) else ""

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def send_json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path); q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if u.path == "/":
                b = open(os.path.join(ROOT, "tools", "workbench.html"), "rb").read()
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
            elif u.path == "/api/pieces":
                self.send_json({"pieces": list_pieces()})
            elif u.path == "/api/version":
                fm, body = split_fm(open(version_path(q["slug"], q["n"]), encoding="utf-8").read())
                self.send_json({"fm": fm, "body": body, "log": coach_log(q["slug"])})
            elif u.path == "/api/status":
                _, st = run(["git", "status", "--short"])
                _, ahead = run(["git", "rev-list", "--count", "@{u}..HEAD"])
                self.send_json({"dirty": st, "ahead": ahead})
            else:
                self.send_json({"error": "not found"}, 404)
        except Exception as e:
            self.send_json({"error": str(e)}, 400)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(n) or b"{}")
        try:
            if self.path == "/api/piece":
                slug, title = data["slug"].strip(), data["title"].strip()
                if not SLUG_RE.match(slug): raise ValueError("slug: lowercase words joined by hyphens")
                if not title: raise ValueError("title required")
                code, out = run(["bin/new-piece", slug, title])
                if code: raise RuntimeError(out)
                self.send_json({"ok": True, "slug": slug})
            elif self.path == "/api/version/save":
                p = version_path(data["slug"], data["n"])
                fm, _ = split_fm(open(p, encoding="utf-8").read())
                if "changes" in data: fm["changes"] = data["changes"]
                open(p, "w", encoding="utf-8").write(join_fm(fm, data["body"]))
                self.send_json({"ok": True, "words": len(data["body"].split())})
            elif self.path == "/api/version/new":
                code, out = run(["bin/new-version", data["slug"]])
                if code: raise RuntimeError(out)
                m = re.search(r"v(\d+)\.md$", out)
                self.send_json({"ok": True, "n": int(m.group(1))})
            elif self.path == "/api/coach":
                slug = data["slug"]; piece_dir(slug)
                dim = data.get("dimension", "").strip()
                ver = f" v{int(data['n'])}" if data.get("n") else ""
                prompt = f"/coach {slug}{ver}" + (f" {dim}" if dim else "")
                code, out = run(["claude", "-p", prompt, "--permission-mode", "acceptEdits", "--output-format", "text"],
                                timeout=600)
                if code: raise RuntimeError(out or "claude exited with error")
                self.send_json({"ok": True, "text": out, "log": coach_log(slug)})
            elif self.path == "/api/commit":
                msg = data.get("message", "").strip() or f"{data['slug']}: save"
                run(["git", "add", "-A"])
                code, out = run(["git", "commit", "-q", "-m", msg])
                self.send_json({"ok": True, "out": out if code else "committed"})
            elif self.path == "/api/publish":
                slug = data["slug"]; piece_dir(slug)
                cmd = ["bin/publish", slug] + ([str(int(data["n"]))] if data.get("n") else [])
                code, out = run(cmd)
                if code: raise RuntimeError(out)
                run(["git", "add", "-A"])
                run(["git", "commit", "-q", "-m", f"{slug}: publish" + (f" v{data['n']}" if data.get('n') else "")])
                code, pout = run(["git", "push"], timeout=120)
                if code: raise RuntimeError(pout)
                self.send_json({"ok": True, "out": out + "\npushed. Live in about 30 s at https://benkaz3.github.io/writing/posts/" + slug + "/"})
            else:
                self.send_json({"error": "not found"}, 404)
        except Exception as e:
            self.send_json({"error": str(e)}, 400)

if __name__ == "__main__":
    srv = HTTPServer(("127.0.0.1", PORT), H)
    url = f"http://127.0.0.1:{PORT}/"
    print(f"Workbench at {url}  (Ctrl+C to stop)")
    if "--no-open" not in sys.argv: webbrowser.open(url)
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
