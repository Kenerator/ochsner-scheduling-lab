"""Fresh supplied-reference state per test, never shared with demo lanes."""
import importlib.util
from pathlib import Path
from http.server import ThreadingHTTPServer
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]

def reference_server():
    spec = importlib.util.spec_from_file_location('reference_api', ROOT/'vendor/reference-api/mock-api/server.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    class QuietHandler(module.Handler):
        store = module.Store()
        def audit(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, QuietHandler.store
