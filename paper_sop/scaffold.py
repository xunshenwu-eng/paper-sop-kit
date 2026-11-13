# -*- coding: utf-8 -*-
"""生成论文项目骨架。"""
import os
from . import stages as S
from . import ledger

TASK_CARD = """# 任务卡 {tid}

## 元数据
- 任务ID：{tid}
- 创建时间：{now}
- 状态：待办
- 所属阶段：{stage}
- 验收标准：（填写可判定的完成条件）

## 目标
{title}

## 输入
- 前置任务：无
- 参考文件：无

## 输出
- 文件名：
- 格式要求：Markdown

## 执行与审核
- 执行：
- 审核：
- 人判点：{human}

## 审核记录
- {now} 创建，待执行
"""

LEDGER = """# 人工断点台账

> 每次需要人做判断、或工具无法自动推进时，在此登记一行；完成后把 `[ ]` 改成 `[x]`。

| 时间 | 断点 | 状态 | 处理人 |
| --- | --- | --- | --- |
| {now} | 项目初始化，S0 契约锁定待本人完成 | 待办 | 本人 |

## 追加记录

"""


def build(root, project):
    os.makedirs(root, exist_ok=True)
    for sid, name, outputs, human in S.STAGES:
        d = os.path.join(root, "stages", f"{sid}-{name}")
        os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(root, "templates"), exist_ok=True)
    t = ledger.now()

    gate_lines = ["# 四层门禁清单", "",
                  "> 每层门禁逐项确认后再推进；L4 未过不得定稿。", ""]
    for gid, (label, items) in S.GATES.items():
        gate_lines += [f"## {gid} · {label}", ""]
        gate_lines += [f"- [ ] {it}" for it in items]
        gate_lines.append("")
    gate_lines += ["## 10 个人判点", ""] + [f"- {p}" for p in S.HUMAN_POINTS] + [""]

    cmd_lines = ["# 常用指令速查", "",
                 "> 12 条通用模板，独立于具体工作台；人判项不交 AI 代理。", "",
                 "| 意图 | 命令 / 动作 |", "| --- | --- |"]
    cmd_lines += [f"| {a} | `{b}` |" for a, b in S.COMMANDS]
    cmd_lines.append("")

    readme = [
        f"# {project}", "",
        "> 由 paper-sop-kit 生成。阶段与门禁由 `sop-state.json` 管理。", "",
        "## 阶段路线", "", "| 阶段 | 名称 | 关键产物 | 人判点 |", "| --- | --- | --- | --- |",
    ]
    for sid, name, outputs, human in S.STAGES:
        readme.append(f"| {sid} | {name} | {', '.join(outputs)} | {human or '—'} |")
    readme += ["", "## 日常操作", "",
               "```bash", "python -m paper_sop status", "python -m paper_sop advance P1",
               "python -m paper_sop gate L1", "python -m paper_sop check", "```", "",
               "## 底线", "",
               "- S0 契约锁定、论证链、最终放行必须本人完成。",
               "- 量化口径当天实测；弱口径显式标注；凭据不内联。",
               "- 三审三查 + B1–B9 任一 ❌ 打回重修，不许带病交付。", ""]

    files = {
        "README.md": "\n".join(readme),
        "todo-ledger.md": LEDGER.format(now=t),
        "gate-checklist.md": "\n".join(gate_lines),
        "commands.md": "\n".join(cmd_lines),
        os.path.join("templates", "task-card.md"): TASK_CARD.format(
            tid="TC-000", now=t, stage="P0", human="本人", title="（任务目标）"),
    }
    for rel, content in files.items():
        with open(os.path.join(root, rel), "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    ledger.save(root, ledger.new_state(project))
    return root


def new_task(root, title, state):
    import re
    p = os.path.join(root, "todo-ledger.md")
    existing = open(p, encoding="utf-8").read() if os.path.isfile(p) else ""
    n = len(re.findall(r"TC-\d+", existing)) + 1
    tid = f"TC-{n:03d}"
    stage = state["stage"] if state else "P0"
    human = S.STAGE_MAP.get(stage, {}).get("human") or "本人"
    content = TASK_CARD.format(tid=tid, now=ledger.now(), stage=stage,
                               human=human, title=title)
    out = os.path.join(root, "stages", f"{stage}-{S.STAGE_MAP[stage]['name']}", f"{tid}.md")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    ledger.append_todo(root, f"{tid} {title}")
    return out
