#!/usr/bin/env python3
"""Render and serve the ICLR 2027 Distill blog preview locally."""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import time

from render import DEFAULT_OUT, DEFAULT_POST, REPO_ROOT, build


def watch_files(post_path: Path, out_dir: Path, interval: float = 1.0) -> None:
    watch_paths = [
        post_path,
        *(REPO_ROOT / "assets" / "bibliography").glob("*.bib"),
    ]
    mtimes = {p: p.stat().st_mtime for p in watch_paths if p.exists()}
    while True:
        time.sleep(interval)
        changed = False
        for p in watch_paths:
            if not p.exists():
                continue
            mtime = p.stat().st_mtime
            if mtimes.get(p) != mtime:
                mtimes[p] = mtime
                changed = True
        if changed:
            print("\nChange detected — rebuilding preview...")
            try:
                build(post_path, out_dir)
            except Exception as exc:
                print(f"Rebuild failed: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and serve the local Distill blog preview.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=4173, help="Bind port (default: 4173).")
    parser.add_argument("--post", type=Path, default=DEFAULT_POST, help="Path to markdown post.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Preview output directory.")
    parser.add_argument("--no-build", action="store_true", help="Serve existing _preview/ without rebuilding.")
    parser.add_argument("--watch", action="store_true", help="Auto-rebuild when the post or bibliography changes.")
    args = parser.parse_args()

    post_path = args.post.resolve()
    out_dir = args.out.resolve()

    if not args.no_build:
        build(post_path, out_dir)

    if args.watch:
        t = threading.Thread(target=watch_files, args=(post_path, out_dir), daemon=True)
        t.start()
        print("Watching post and bibliography for changes (reload browser after saving)...")

    handler = partial(SimpleHTTPRequestHandler, directory=str(out_dir))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving preview at http://{args.host}:{args.port}/ (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
