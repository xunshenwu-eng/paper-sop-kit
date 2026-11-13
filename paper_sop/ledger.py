# -*- coding: utf-8 -*-
"""状态文件读写。纯 JSON，可手工编辑。"""
import os, json, datetime

STATE_NAME = "sop-state.json"


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def new_state(project):
    t = now()
    return {"project": project, "stage": "P0", "completed": [],
            "gates": {}, "created": t, "updated": t}


def load(root):
    p = os.path.join(root, STATE_NAME)
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(root, state):
    state["updated"] = now()
    p = os.path.join(root, STATE_NAME)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    return p


def append_todo(root, text):
    p = os.path.join(root, "todo-ledger.md")
    line = f"- [ ] {now()}  {text}\n"
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(line)
    return p
