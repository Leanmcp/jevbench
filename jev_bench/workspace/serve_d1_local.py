# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "transformers>=5.19.0",
#     "torch>=2.14.1",
#     "torchvision>=0.29.1",
#     "pillow>=12.3.0",
# ]
# ///
"""Serve an open-weight Liquid d1 model on loopback for run_eval.py.

No hosted API serves d1-3B or d1-omni-600M, so this is the one place the
benchmark runs weights itself. Both are small enough for a laptop: Apple
silicon (MPS) or any CUDA GPU, CPU as a slow fallback.

    uv run workspace/serve_d1_local.py --model LiquidAI/d1-3B
    uv run workspace/serve_d1_local.py --model LiquidAI/d1-omni-600M

Then, in another shell:

    uv run workspace/run_eval.py --endpoint d1local --no-send-model --label d1-3B

The request body is the harness's own {state, questions}; the reply is what
model.system_one returns, {answers, usage}, plus the served model id. Calls
are serialised under one lock because a single model instance is not safe to
share across threads; run_eval's concurrency only queues requests here.
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import torch
from transformers import AutoModel


def load(model_id: str, revision: str | None):
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    dtype = torch.float32 if device == "cpu" else torch.bfloat16
    model = AutoModel.from_pretrained(model_id, trust_remote_code=True, dtype=dtype, revision=revision).to(device)
    model.eval()
    return model, device, str(dtype).replace("torch.", "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="LiquidAI/d1-3B", help="LiquidAI/d1-3B or LiquidAI/d1-omni-600M")
    ap.add_argument("--revision", default=None, help="pin a Hugging Face commit hash for a reproducible run")
    ap.add_argument("--port", type=int, default=18100)
    args = ap.parse_args()

    t0 = time.time()
    model, device, dtype = load(args.model, args.revision)
    served = f"{args.model}@{args.revision or 'main'}"
    print(f"loaded {served} on {device} ({dtype}) in {time.time() - t0:.1f}s")
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            # matrix.py checks this so a d1-3B cell never runs against omni.
            if self.path == "/health":
                self._send(200, {"ok": True, "model": served})
            else:
                self._send(404, {"error": f"unknown path {self.path}"})

        def do_POST(self) -> None:
            if self.path != "/v1/request":
                self._send(404, {"error": f"unknown path {self.path}"})
                return
            try:
                req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                state, questions = req.get("state"), req["questions"]
            except (ValueError, KeyError) as exc:
                self._send(400, {"error": f"bad request: {exc}"})
                return
            try:
                with lock, torch.inference_mode():
                    out = model.system_one(state, questions)
            except Exception as exc:  # report the model's own error to the client
                self._send(422, {"error": f"{type(exc).__name__}: {exc}"})
                return
            self._send(200, {**out, "model": served})

        def log_message(self, fmt: str, *a) -> None:
            pass  # run_eval prints progress; per-request lines would drown it

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"serving on http://127.0.0.1:{args.port}/v1/request  (ctrl-c to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
