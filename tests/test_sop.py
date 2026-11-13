# -*- coding: utf-8 -*-
import os, sys, json, tempfile, unittest, contextlib, io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paper_sop import cli, stages as S, ledger, scaffold, gates


class TestModel(unittest.TestCase):
    def test_eight_stages(self):
        self.assertEqual(len(S.STAGE_IDS), 8)
        self.assertEqual(S.STAGE_IDS[0], "P0")
        self.assertEqual(S.STAGE_IDS[-1], "P7")

    def test_four_gates(self):
        self.assertEqual(set(S.GATES), {"L1", "L2", "L3", "L4"})

    def test_ten_human_points(self):
        self.assertEqual(len(S.HUMAN_POINTS), 10)
        self.assertTrue(any("S0" in p for p in S.HUMAN_POINTS))

    def test_nine_must_pass(self):
        self.assertEqual(len(S.MUST_PASS), 9)


class TestScaffold(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.d.name, "thesis")
        scaffold.build(self.root, "测试论文")

    def tearDown(self):
        self.d.cleanup()

    def test_files_created(self):
        for f in ("sop-state.json", "README.md", "todo-ledger.md",
                  "gate-checklist.md", "commands.md", "templates/task-card.md"):
            self.assertTrue(os.path.isfile(os.path.join(self.root, f)), f)

    def test_eight_stage_dirs(self):
        for sid, name, _, _ in S.STAGES:
            self.assertTrue(os.path.isdir(os.path.join(self.root, "stages", f"{sid}-{name}")))

    def test_state_initial(self):
        st = ledger.load(self.root)
        self.assertEqual(st["stage"], "P0")
        self.assertEqual(st["completed"], [])


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.d.name, "thesis")
        scaffold.build(self.root, "测试论文")
        self.old = os.getcwd()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.old)
        self.d.cleanup()

    def test_status(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(cli.main(["status"]), 0)
        self.assertIn("P0", buf.getvalue())

    def test_advance_ok(self):
        self.assertEqual(cli.main(["advance", "P1"]), 0)
        self.assertEqual(ledger.load(self.root)["stage"], "P1")

    def test_advance_no_skip(self):
        self.assertEqual(cli.main(["advance", "P3"]), 1)
        self.assertEqual(ledger.load(self.root)["stage"], "P0")

    def test_advance_unknown(self):
        self.assertEqual(cli.main(["advance", "P9"]), 2)

    def test_gate_blocked_early(self):
        self.assertEqual(cli.main(["gate", "L4"]), 1)

    def test_gate_l1(self):
        self.assertEqual(cli.main(["gate", "L1"]), 0)
        self.assertTrue(ledger.load(self.root)["gates"]["L1"])

    def test_task_card(self):
        self.assertEqual(cli.main(["task", "new", "补三篇文献"]), 0)
        p = os.path.join(self.root, "stages", "P0-选题", "TC-001.md")
        self.assertTrue(os.path.isfile(p))
        with open(p, encoding="utf-8") as f:
            self.assertIn("补三篇文献", f.read())

    def test_check_ok(self):
        self.assertEqual(cli.main(["check"]), 0)


class TestNotProject(unittest.TestCase):
    def test_missing_state(self):
        with tempfile.TemporaryDirectory() as d:
            old = os.getcwd()
            os.chdir(d)
            try:
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(cli.main(["status"]), 2)
            finally:
                os.chdir(old)


if __name__ == "__main__":
    unittest.main(verbosity=2)
