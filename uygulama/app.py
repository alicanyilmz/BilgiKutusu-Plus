#!/usr/bin/env python3
"""BilgiKutusu Plus: trusted-LAN, read-only file depot. Python 3.9+, Linux.

Copyright (c) 2026 Ali Can Yılmaz. See LICENSE.
"""
import argparse
import contextlib
import json
import logging
import os
from pathlib import Path
import re
import stat
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, unquote, urlsplit

VERSION = "1.0.0"
WEB = Path(__file__).resolve().parent / "web"
SAFE_TYPES = {
    ".pdf": "application/pdf", ".txt": "text/plain; charset=utf-8",
    ".md": "text/plain; charset=utf-8", ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif",
    ".webp": "image/webp", ".mp3": "audio/mpeg", ".ogg": "audio/ogg",
    ".wav": "audio/wav", ".mp4": "video/mp4", ".webm": "video/webm",
}
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/favicon.svg": ("favicon.svg", "image/svg+xml"),
}


class DepotError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


def parts_for(path):
    if len(path) > 4096 or "\\" in path or any(ord(c) < 32 for c in path):
        raise DepotError(400, "Geçersiz dosya yolu.")
    if path.startswith("/"):
        raise DepotError(403, "Bu yola erişilemez.")
    parts = path.split("/") if path else []
    if any(not p or p.startswith(".") for p in parts):
        raise DepotError(403, "Gizli dosyalara ve üst dizinlere erişilemez.")
    return parts


class Depot:
    def __init__(self, root, max_entries=2000):
        self.root = Path(root).resolve(strict=True)
        if not self.root.is_dir() or self.root == Path("/"):
            raise ValueError("İçerik için ayrı bir klasör seçin.")
        self.max_entries = max_entries

    @contextlib.contextmanager
    def open(self, relative, directory=False):
        """Walk directory descriptors; no symbolic links, even during a rename race."""
        parts = parts_for(relative)
        fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for i, part in enumerate(parts):
                flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
                if directory or i < len(parts) - 1:
                    flags |= os.O_DIRECTORY
                next_fd = os.open(part, flags, dir_fd=fd)
                os.close(fd)
                fd = next_fd
            info = os.fstat(fd)
            if directory and not stat.S_ISDIR(info.st_mode):
                raise DepotError(404, "Klasör bulunamadı.")
            if not directory and not stat.S_ISREG(info.st_mode):
                raise DepotError(404, "Dosya bulunamadı.")
            yield fd, info
        finally:
            os.close(fd)

    def listing(self, path):
        entries = []
        with self.open(path, directory=True) as (fd, _):
            with os.scandir(fd) as iterator:
                for item in iterator:
                    if "\\" in item.name or item.name.startswith(".") or any(ord(c) < 32 for c in item.name):
                        continue
                    try:
                        item.name.encode("utf-8")
                        info = item.stat(follow_symlinks=False)
                    except (OSError, UnicodeError):
                        continue
                    is_dir = stat.S_ISDIR(info.st_mode)
                    if not is_dir and not stat.S_ISREG(info.st_mode):
                        continue
                    relative = "/".join(filter(None, [path, item.name]))
                    entries.append({
                        "name": item.name, "path": relative,
                        "directory": is_dir, "size": None if is_dir else info.st_size,
                        "modified": int(info.st_mtime),
                        "url": "/files/" + quote(relative, safe="/"),
                    })
                    if len(entries) > self.max_entries:
                        raise DepotError(413, "Bu klasör çok kalabalık. Dosyaları alt klasörlere ayırın.")
        entries.sort(key=lambda x: (not x["directory"], x["name"].casefold()))
        return {"path": path, "entries": entries, "version": VERSION}


def byte_range(value, size):
    """Single HTTP byte range, including suffix ranges. None means whole file."""
    if value is None:
        return None
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", value.strip())
    if not match or not any(match.groups()) or size == 0:
        raise DepotError(416, "Geçersiz dosya aralığı.")
    left, right = match.groups()
    try:
        if not left:
            length = int(right)
            if length <= 0:
                raise ValueError
            start, end = max(0, size - length), size - 1
        else:
            start = int(left)
            end = min(int(right), size - 1) if right else size - 1
            if start >= size or start > end:
                raise ValueError
    except ValueError:
        raise DepotError(416, "Geçersiz dosya aralığı.") from None
    return start, end


class PlusServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 16

    def __init__(self, address, depot, max_clients=8):
        self.depot = depot
        self.slots = threading.BoundedSemaphore(max_clients)
        super().__init__(address, PlusHandler)

    def get_request(self):
        sock, addr = super().get_request()
        sock.settimeout(15)
        return sock, addr

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            try:
                request.sendall(b"HTTP/1.0 503 Service Unavailable\r\nContent-Length: 0\r\nRetry-After: 3\r\nConnection: close\r\n\r\n")
            except OSError:
                pass
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()

    def handle_error(self, request, client_address):
        # The default handler prints client addresses and exception details.
        logging.error("Bir bağlantı işlenemedi; istek ayrıntıları kaydedilmedi.")


class PlusHandler(BaseHTTPRequestHandler):
    server_version = "BilgiKutusuPlus/" + VERSION
    sys_version = ""

    def log_message(self, fmt, *args):
        # Access logging is disabled: no client IP, URL, headers or filenames.
        return

    def respond_headers(self, status, content_type, length, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'self'; form-action 'none'")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()

    def json(self, data, status=200, extra=None):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.respond_headers(status, "application/json; charset=utf-8", len(body), extra)
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        try:
            self.route()
        except DepotError as exc:
            self.json({"error": exc.message}, exc.status)
        except FileNotFoundError:
            self.json({"error": "Dosya veya klasör bulunamadı."}, 404)
        except PermissionError:
            self.json({"error": "Bu içeriği okumak için izin yok."}, 403)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass
        except OSError:
            self.json({"error": "İçerik açılamadı. Bağlantıları ve dosya izinlerini kontrol edin."}, 403)
        except (ValueError, UnicodeError):
            self.json({"error": "Geçersiz istek."}, 400)

    def route(self):
        if len(self.path) > 8192:
            raise DepotError(414, "Adres çok uzun.")
        url = urlsplit(self.path)
        query = parse_qs(url.query, max_num_fields=10)
        if url.path in STATIC:
            name, mime = STATIC[url.path]
            body = (WEB / name).read_bytes()
            self.respond_headers(200, mime, len(body))
            if self.command != "HEAD":
                self.wfile.write(body)
        elif url.path == "/api/list":
            self.json(self.server.depot.listing(query.get("path", [""])[0]))
        elif url.path == "/api/health":
            with self.server.depot.open("", directory=True):
                self.json({"ok": True, "version": VERSION})
        elif url.path.startswith("/files/"):
            relative = unquote(url.path[len("/files/"):], errors="strict")
            self.send_content(relative, query.get("download", [""])[0] == "1")
        else:
            raise DepotError(404, "Sayfa bulunamadı.")

    def send_content(self, path, download):
        with self.server.depot.open(path) as (fd, info):
            try:
                selection = byte_range(self.headers_in_range(), info.st_size)
            except DepotError as exc:
                self.json({"error": exc.message}, 416, {"Content-Range": f"bytes */{info.st_size}"})
                return
            start, end = selection if selection else (0, info.st_size - 1)
            length = max(0, end - start + 1)
            mime = SAFE_TYPES.get(Path(path).suffix.lower(), "application/octet-stream")
            disposition = "attachment" if download or mime == "application/octet-stream" else "inline"
            extra = {"Accept-Ranges": "bytes", "Content-Disposition": f"{disposition}; filename*=UTF-8''{quote(Path(path).name, safe='')}"}
            if selection:
                extra["Content-Range"] = f"bytes {start}-{end}/{info.st_size}"
            self.respond_headers(206 if selection else 200, mime, length, extra)
            if self.command == "HEAD":
                return
            os.lseek(fd, start, os.SEEK_SET)
            while length:
                block = os.read(fd, min(65536, length))
                if not block:
                    break
                self.wfile.write(block)
                length -= len(block)

    def headers_in_range(self):
        # BaseHTTPRequestHandler stores incoming headers in self.headers.
        return self.headers.get("Range")


def load_config(filename):
    config_path = Path(filename).resolve()
    with config_path.open(encoding="utf-8") as handle:
        cfg = json.load(handle)
    if not isinstance(cfg, dict):
        raise ValueError("Ayar dosyası bir JSON nesnesi olmalı.")
    content_dir = cfg.get("content_dir", "icerik")
    if not isinstance(content_dir, str) or not content_dir.strip():
        raise ValueError("content_dir boş olmayan bir klasör yolu olmalı.")
    root = Path(content_dir)
    if not root.is_absolute():
        root = config_path.parent / root
    host, port = cfg.get("host", "127.0.0.1"), cfg.get("port", 8091)
    clients, entries = cfg.get("max_clients", 8), cfg.get("max_entries", 2000)
    if not isinstance(host, str) or not host:
        raise ValueError("Geçersiz dinleme adresi.")
    if type(port) is not int or not 1024 <= port <= 65535:
        raise ValueError("Port 1024–65535 arasında olmalı.")
    if type(clients) is not int or not 1 <= clients <= 32:
        raise ValueError("max_clients 1–32 arasında olmalı.")
    if type(entries) is not int or not 1 <= entries <= 10000:
        raise ValueError("max_entries 1–10000 arasında olmalı.")
    return host, port, Depot(root, entries), clients


def main():
    parser = argparse.ArgumentParser(description="BilgiKutusu Plus yerel bilgi deposu")
    parser.add_argument("--config", default=str(Path(__file__).resolve().parent.parent / "ayarlar" / "config.json"))
    parser.add_argument("--check", action="store_true", help="Ayar ve içerik klasörünü denetle")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        host, port, depot, clients = load_config(args.config)
        with depot.open("", directory=True):
            pass
        if args.check:
            print("Ayar dosyası ve içerik klasörü kullanılabilir.")
            return 0
        with PlusServer((host, port), depot, clients) as server:
            print(f"BilgiKutusu Plus {VERSION} | {host}:{port}", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except (OSError, ValueError, DepotError) as exc:
        logging.error("Başlatılamadı: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
