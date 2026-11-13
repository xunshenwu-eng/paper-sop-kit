# -*- coding: utf-8 -*-
"""门禁自检：只做确定性检查，质量判断留给人。"""
import os
from . import stages as S


def check_gate(root, gid, state):
    label, items = S.GATES[gid]
    findings = []
    for f in ("README.md", "todo-ledger.md", "gate-checklist.md", "commands.md"):
        if not os.path.isfile(os.path.join(root, f)):
            findings.append(f"缺文件: {f}")
    if gid == "L4":
        rec = os.path.join(root, "stages", "P6-审查", "三审三查记录.md")
        if not os.path.isfile(rec):
            findings.append("L4 需 P6 审查记录（三审三查记录.md）")
    if gid in ("L2", "L3", "L4") and state and state.get("stage") in ("P0", "P1"):
        findings.append(f"当前阶段 {state['stage']}，尚未到内容生产，门禁条件不足")
    return {"gate": gid, "label": label, "items": items,
            "blocking": findings, "ready": not findings}


def delivery_checklist(root, state):
    out = {"three_reviews": S.THREE_REVIEWS, "three_checks": S.THREE_CHECKS,
           "must_pass": S.MUST_PASS, "human_points": S.HUMAN_POINTS,
           "missing_files": [], "notes": []}
    for f in ("README.md", "todo-ledger.md", "gate-checklist.md"):
        if not os.path.isfile(os.path.join(root, f)):
            out["missing_files"].append(f)
    if state and state["stage"] != "P7":
        out["notes"].append(f"当前 {state['stage']}，最终放行需推进到 P7")
    out["notes"].append("以下各项必须人工确认，工具不代判")
    return out
