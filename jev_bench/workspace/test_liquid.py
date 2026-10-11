"""Offline contract checks; run with uv run workspace/test_liquid.py."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import common as C
from run_eval import load_done, resolve_endpoint


class LiquidContractTests(unittest.TestCase):
    def test_endpoint_and_auth_are_provider_specific(self):
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "jev-secret", "LIQUID_API_KEY": "liquid-secret"}, clear=True):
            client = C.DecisionClient(resolve_endpoint("liquid"), C.LIQUID_MODEL)
            self.assertEqual(client.endpoint, "https://api.liquid.ai/decisions/v1/systemone")
            self.assertEqual(client._key, "liquid-secret")
            self.assertEqual(C.DecisionClient()._key, "jev-secret")
            self.assertEqual(C._scrub("jev-secret liquid-secret"), "[redacted] [redacted]")

    def test_jev_key_cannot_substitute_for_liquid_key(self):
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "jev-secret"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "LIQUID_API_KEY"):
                C.DecisionClient(C.LIQUID_URL, C.LIQUID_MODEL)
            C.DecisionClient(C.LIQUID_URL, C.LIQUID_MODEL, require_key=False)

    def test_request_keeps_input_and_excludes_gold(self):
        case = {"state": {"message": "hello"}, "question_key": "q",
                "question": C.noul_q("Is this spam?", "Spam", "Not spam"), "gold": False}
        client = C.DecisionClient(C.LIQUID_URL, C.LIQUID_MODEL, require_key=False)
        self.assertEqual(client.build_request(case), {
            "model": "d1:free", "state": case["state"], "questions": {"q": case["question"]}})

    def test_documented_response_shapes_and_zero_tokens(self):
        examples = [
            ("noul", {"type": "noul", "noul": 0.999}, "p_true", 0.999),
            ("choice", {"type": "choice", "choice": "billing",
                        "probabilities": {"billing": 0.8, "account": 0.2}, "confidence": 0.6}, "pred", "billing"),
            ("score", {"type": "score", "score": 1.8,
                       "probabilities": {"0": 0.0, "1": 0.2, "2": 0.8}}, "expected_level", 1.8),
        ]
        for kind, answer, field, expected in examples:
            with self.subTest(kind=kind):
                payload = {"model": "d1:free", "answers": {"q": answer},
                           "usage": {"input_tokens": 84, "output_tokens": 0}}
                self.assertEqual(C.parse_answer(payload, "q", kind)[field], expected)
                self.assertEqual(C.usage_of(payload)["output_tokens"], 0)

    def test_resume_retries_parse_failures(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "predictions.jsonl"
            C.jsonl_append(path, [
                {"case_id": "bad", "error": None, "parse_error": "missing answer"},
                {"case_id": "good", "error": None},
            ])
            self.assertEqual(load_done(path), {"good"})


if __name__ == "__main__":
    unittest.main()
