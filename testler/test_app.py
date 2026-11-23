"""Integration checks using real HTTP requests and temporary content."""
import http.client
import contextlib
import io
import json
import logging
import os
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.parse import quote
from unittest.mock import patch

from uygulama import app


class DepotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "content"
        self.root.mkdir()
        (self.root / "Belgeler").mkdir()
        (self.root / "Bos").mkdir()
        (self.root / "Belgeler" / "Türkçe boşluk.txt").write_text("Merhaba Dünya!", encoding="utf-8")
        (self.root / "bytes.mp4").write_bytes(b"0123456789abcdef")
        (self.root / "empty.txt").touch()
        (self.root / "active.html").write_text("<script>alert(1)</script>")
        (self.root / "image.svg").write_text("<svg/>")
        (self.root / ".secret").write_text("hidden")
        outside = Path(self.temp.name) / "private.txt"
        outside.write_text("PRIVATE")
        (self.root / "leak.txt").symlink_to(outside)
        (self.root / "linked-dir").symlink_to(self.root / "Belgeler", target_is_directory=True)
        self.server = app.PlusServer(("127.0.0.1", 0), app.Depot(self.root))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, path, method="GET", headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            conn.request(method, path, headers=headers or {})
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            conn.close()

    def test_home_and_local_assets(self):
        for path in ("/", "/style.css", "/app.js", "/favicon.svg"):
            with self.subTest(path=path):
                status, headers, body = self.request(path)
                self.assertEqual(status, 200)
                self.assertEqual(int(headers["Content-Length"]), len(body))
                self.assertIn("default-src 'self'", headers["Content-Security-Policy"])

    def test_health(self):
        status, _, body = self.request("/api/health")
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["ok"])

    def test_requests_do_not_log_private_details(self):
        output = io.StringIO()
        handler = logging.StreamHandler(output)
        logger = logging.getLogger()
        previous_level = logger.level
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        try:
            with contextlib.redirect_stderr(output):
                self.assertEqual(self.request("/api/list?note=privacy-marker", headers={"Authorization":"Bearer test-marker"})[0], 200)
                self.assertEqual(self.request("/files/nonexistent-private-file.txt")[0], 404)
            self.assertEqual(output.getvalue(), "")
        finally:
            logger.removeHandler(handler)
            logger.setLevel(previous_level)

    def test_unexpected_error_does_not_print_request_details(self):
        output = io.StringIO()
        handler = logging.StreamHandler(output)
        logger = logging.getLogger()
        logger.addHandler(handler)
        try:
            with contextlib.redirect_stderr(output), patch.object(app.PlusHandler, "route", side_effect=RuntimeError("private-error-marker")):
                with self.assertRaises(http.client.RemoteDisconnected):
                    self.request("/api/list?note=private-url-marker")
            logged = output.getvalue()
            for value in ("127.0.0.1", "private-error-marker", "private-url-marker", "Traceback"):
                self.assertNotIn(value, logged)
        finally:
            logger.removeHandler(handler)

    def test_directory_list_hides_private_and_symlinks(self):
        status, _, body = self.request("/api/list")
        self.assertEqual(status, 200)
        names = {entry["name"] for entry in json.loads(body)["entries"]}
        self.assertIn("Belgeler", names)
        self.assertNotIn(".secret", names)
        self.assertNotIn("leak.txt", names)
        self.assertNotIn("linked-dir", names)

    def test_turkish_name_and_download(self):
        path = "/files/" + quote("Belgeler/Türkçe boşluk.txt")
        status, headers, body = self.request(path + "?download=1")
        self.assertEqual(status, 200)
        self.assertEqual(body.decode(), "Merhaba Dünya!")
        self.assertIn("attachment", headers["Content-Disposition"])
        self.assertIn("filename*=UTF-8''", headers["Content-Disposition"])

    def test_nesting_and_empty_folder(self):
        for folder, size in (("Belgeler", 1), ("Bos", 0)):
            status, _, body = self.request("/api/list?path=" + folder)
            self.assertEqual(status, 200)
            self.assertEqual(len(json.loads(body)["entries"]), size)

    def test_missing_path_and_config_private(self):
        for path in ("/not-found", "/config.json", "/app.py", "/files/missing.txt", "/api/list?path=missing"):
            with self.subTest(path=path): self.assertEqual(self.request(path)[0], 404)

    def test_traversal_and_hidden_names(self):
        for path in ("/files/../private.txt", "/files/%2e%2e/private.txt", "/files/.secret", "/files/%2Fetc/passwd", "/api/list?path=..", "/api/list?path=%2Fetc", "/api/list?path=Belgeler%2F.."):
            with self.subTest(path=path): self.assertEqual(self.request(path)[0], 403)

    def test_symlinks_never_serve(self):
        for path in ("/files/leak.txt", "/api/list?path=linked-dir", "/files/linked-dir/"+quote("Türkçe boşluk.txt")):
            with self.subTest(path=path): self.assertIn(self.request(path)[0], (403,404))

    def test_control_characters_and_backslash_rejected(self):
        for path in ("/files/a%00b", "/api/list?path=a%5Cb"):
            self.assertEqual(self.request(path)[0], 400)

    def test_active_content_forced_download(self):
        for filename in ("active.html", "image.svg"):
            status, headers, _ = self.request("/files/"+filename)
            self.assertEqual(status, 200)
            self.assertEqual(headers["Content-Type"], "application/octet-stream")
            self.assertTrue(headers["Content-Disposition"].startswith("attachment"))
            self.assertEqual(headers["X-Content-Type-Options"], "nosniff")

    def test_ranges(self):
        for header, expected, content_range in (("bytes=2-5", b"2345", "bytes 2-5/16"), ("bytes=12-", b"cdef", "bytes 12-15/16"), ("bytes=-3", b"def", "bytes 13-15/16"), ("bytes=14-999", b"ef", "bytes 14-15/16")):
            with self.subTest(header=header):
                status, headers, body = self.request("/files/bytes.mp4", headers={"Range":header})
                self.assertEqual((status,body), (206,expected))
                self.assertEqual(headers["Content-Range"], content_range)

    def test_invalid_ranges(self):
        for header in ("bytes=99-", "bytes=9-2", "bytes=-0", "bytes=0-1,3-4", "garbage"):
            with self.subTest(header=header):
                status, headers, _ = self.request("/files/bytes.mp4", headers={"Range":header})
                self.assertEqual(status,416)
                self.assertEqual(headers["Content-Range"],"bytes */16")

    def test_empty_file(self):
        status, headers, body = self.request("/files/empty.txt")
        self.assertEqual((status,body),(200,b""))
        self.assertEqual(headers["Content-Length"],"0")
        self.assertEqual(self.request("/files/empty.txt",headers={"Range":"bytes=0-"})[0],416)

    def test_head_has_no_body(self):
        status, headers, body = self.request("/files/bytes.mp4",method="HEAD")
        self.assertEqual((status,body),(200,b""))
        self.assertEqual(headers["Content-Length"],"16")

    def test_write_methods_disabled(self):
        self.assertEqual(self.request("/files/new.txt",method="POST")[0],501)
        self.assertEqual(self.request("/files/bytes.mp4",method="DELETE")[0],501)
        self.assertFalse((self.root/"new.txt").exists())
        self.assertTrue((self.root/"bytes.mp4").exists())

    def test_too_many_files_clear_error(self):
        self.server.depot.max_entries = 1
        status, _, body = self.request("/api/list")
        self.assertEqual(status,413)
        self.assertIn("alt klasör",json.loads(body)["error"])

    def test_invalid_content_directory_types(self):
        config = Path(self.temp.name) / "invalid.json"
        for value in (None, True, 123, [], {}, "", "   "):
            with self.subTest(value=value):
                config.write_text(json.dumps({"content_dir": value}))
                with self.assertRaises(ValueError):
                    app.load_config(config)

    def test_unopenable_backslash_filename_hidden(self):
        (self.root / "bad\\name.txt").write_text("test")
        status, _, body = self.request("/api/list")
        self.assertEqual(status, 200)
        self.assertNotIn("bad\\name.txt", {e["name"] for e in json.loads(body)["entries"]})

    def test_packaged_defaults(self):
        project = Path(app.__file__).resolve().parent.parent
        host, port, depot, clients = app.load_config(project / "ayarlar/config.json")
        self.assertEqual(host, "127.0.0.1")
        self.assertEqual(port, 8091)
        self.assertTrue((depot.root / "Belgeler/Baslangic.txt").is_file())
        for name, _ in app.STATIC.values():
            self.assertTrue((app.WEB / name).is_file())

    def test_relative_configuration(self):
        config = Path(self.temp.name)/"config.json"
        config.write_text(json.dumps({"content_dir":"content", "port":8091}))
        host, port, depot, clients = app.load_config(config)
        self.assertEqual((host,port,clients),("127.0.0.1",8091,8))
        self.assertEqual(depot.root,self.root)
        config.write_text(json.dumps({"port":True}))
        with self.assertRaises(ValueError): app.load_config(config)


if __name__ == "__main__":
    unittest.main()
