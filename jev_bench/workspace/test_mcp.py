"""Offline MCP regression checks. Run yourself: uv run workspace/test_mcp.py."""
import copy
import unittest

import build_mcp_cases as M
import common as C
import score_runs as S


class MCPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, cls.tasks = M.build(permute=True)

    def test_pinned_coverage_and_unique_ids(self):
        expected = {"mcpmark_server_routing": 127, "mcpbench_server_routing": 56,
                    "mcpmark_tool_selection": 9, "mcpbench_tool_selection": 13}
        ids = []
        for key, count in expected.items():
            rows = self.cases[key]
            self.assertEqual(len(rows), count * 2)
            ids.extend(c["case_id"] for c in rows)
            for c in rows:
                self.assertIn(c["gold"], c["question"]["criteria"])
                self.assertFalse(c["truncated"])
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(self.tasks["mcpbench"]), 104)

    def test_allowlisted_input_and_provider_parity(self):
        jev = C.DecisionClient(C.JEV_URL, C.JEV_MODEL, require_key=False)
        d1 = C.DecisionClient(C.LIQUID_URL, C.LIQUID_MODEL, require_key=False)
        for rows in self.cases.values():
            for case in rows:
                a, b = jev.build_request(case), d1.build_request(case)
                a.pop("model")
                b.pop("model")
                self.assertEqual(a, b)
                expected = {"task", "decision_checkpoint"} if case["metric_scope"] == "tool_selection" else {"task"}
                self.assertEqual(set(a["state"]), expected)
                self.assertNotIn("gold", a)
                self.assertNotIn("label_evidence", a)
                if case["source"] == "mcpbench":
                    task = self.tasks["mcpbench"][case["source_task"]]
                    self.assertEqual(a["state"]["task"], task["prompt"])

    def test_mcpmark_directory_aliases_do_not_duplicate_postgres(self):
        tasks = self.tasks["mcpmark"]
        self.assertEqual(len(tasks), 177)  # 127 standard + 50 easy
        self.assertFalse(any(key.startswith(("insforge/", "supabase/")) for key in tasks))
        standard_postgres = [key for key in tasks if key.startswith("postgres/standard/")]
        self.assertEqual(len(standard_postgres), 21)
        routing = self.cases["mcpmark_server_routing"]
        self.assertEqual(len({c["source_task"] for c in routing if c["gold"] == "postgres"}), 21)
        self.assertEqual(set(routing[0]["question"]["criteria"]),
                         {"filesystem", "github", "notion", "postgres",
                          "playwright", "playwright_webarena"})

    def test_order_variants_keep_gold_and_task_families(self):
        for rows in self.cases.values():
            for base, twin in zip(rows[::2], rows[1::2]):
                self.assertEqual(base["gold"], twin["gold"])
                self.assertEqual(base["family_id"], twin["family_id"])
                self.assertEqual(base["state"], twin["state"])
                self.assertNotEqual(list(base["question"]["criteria"]), list(twin["question"]["criteria"]))
                self.assertEqual(base["question"]["criteria"], twin["question"]["criteria"])

    def test_choice_scoring_counts_wrong_tool(self):
        c = self.cases["mcpbench_tool_selection"][0]
        wrong = next(k for k in c["question"]["criteria"] if k != c["gold"])
        scores = S.score_choice([{"gold": c["gold"], "pred": c["gold"]},
                                 {"gold": c["gold"], "pred": wrong}])
        self.assertEqual(scores["accuracy"], 0.5)

    def test_checkpoint_edit_changes_case_identity(self):
        c = self.cases["mcpbench_tool_selection"][0]
        state = copy.deepcopy(c["state"])
        state["decision_checkpoint"] += " Changed."
        spec = M.read_json(M.MANIFEST)["sources"]["mcpbench"]
        new = M.make_case("mcpbench", c["source_task"], "overview", state,
                          c["question"]["criteria"], c["gold"], "tool_selection",
                          self.tasks["mcpbench"][c["source_task"]], spec, c["label_evidence"])
        self.assertNotEqual(c["case_id"], new["case_id"])


if __name__ == "__main__":
    unittest.main()
