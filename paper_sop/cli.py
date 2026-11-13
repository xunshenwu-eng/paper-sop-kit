# -*- coding: utf-8 -*-
import os, sys, argparse
from . import stages as S, ledger, scaffold, gates


def _state(root):
    st = ledger.load(root)
    if st is None:
        print("当前目录不是 sop 项目（缺 sop-state.json）。先运行: python -m paper_sop init <name>",
              file=sys.stderr)
        return None
    return st


def main(argv=None):
    ap = argparse.ArgumentParser(prog="paper-sop", description="论文流程脚手架（零依赖）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="生成论文项目骨架")
    i.add_argument("name")
    i.add_argument("--dir", help="目标目录，默认 ./<name>")

    a2 = sub.add_parser("advance", help="推进到下一阶段")
    a2.add_argument("stage")

    g = sub.add_parser("gate", help="校验某层门禁")
    g.add_argument("level", choices=list(S.GATES))

    t = sub.add_parser("task", help="新建任务卡")
    t.add_argument("action", choices=["new"])
    t.add_argument("title")

    sub.add_parser("status", help="查看状态")
    sub.add_parser("check", help="交付清单自检")
    a = ap.parse_args(argv)

    if a.cmd == "init":
        root = a.dir or os.path.join(os.getcwd(), a.name)
        scaffold.build(root, a.name)
        print(f"✅ 已生成项目骨架: {root}")
        print(f"   阶段 {len(S.STAGE_IDS)} 个 / 门禁 {len(S.GATES)} 层 / 人判点 {len(S.HUMAN_POINTS)} 个")
        print("   下一步: cd 到该目录后运行 python -m paper_sop status")
        return 0

    root = os.getcwd()
    st = _state(root)
    if st is None:
        return 2

    if a.cmd == "status":
        print(f"项目   {st['project']}")
        print(f"阶段   {st['stage']} · {S.STAGE_MAP[st['stage']]['name']}")
        print(f"已完成 {' → '.join(st['completed']) or '（无）'}")
        print(f"门禁   {', '.join(k + ':' + ('✅' if v else '⬜') for k, v in st['gates'].items()) or '（未记录）'}")
        hp = S.STAGE_MAP[st["stage"]]["human"]
        print(f"人判点 {hp or '本阶段无'}")
        print(f"更新   {st['updated']}")
        return 0

    if a.cmd == "advance":
        target = a.stage.upper()
        if target not in S.STAGE_IDS:
            print(f"未知阶段: {target}", file=sys.stderr)
            return 2
        cur_idx = S.STAGE_IDS.index(st["stage"])
        tgt_idx = S.STAGE_IDS.index(target)
        if tgt_idx != cur_idx + 1:
            print(f"禁止跳级：当前 {st['stage']}，只能推进到 {S.STAGE_IDS[cur_idx + 1] if cur_idx + 1 < len(S.STAGE_IDS) else '（已到末阶段）'}",
                  file=sys.stderr)
            return 1
        st["completed"].append(st["stage"])
        st["stage"] = target
        ledger.save(root, st)
        ledger.append_todo(root, f"推进到 {target} · {S.STAGE_MAP[target]['name']}")
        print(f"✅ 已推进到 {target} · {S.STAGE_MAP[target]['name']}")
        hp = S.STAGE_MAP[target]["human"]
        if hp:
            print(f"⚠️ 人判点：{hp}")
        return 0

    if a.cmd == "gate":
        r = gates.check_gate(root, a.level, st)
        print(f"{r['gate']} · {r['label']}")
        for it in r["items"]:
            print("  - [ ] " + it)
        if r["blocking"]:
            print("阻断项：")
            for x in r["blocking"]:
                print("  ❌ " + x)
            return 1
        print("✅ 结构检查通过；逐项内容确认仍需人工完成")
        st["gates"][a.level] = True
        ledger.save(root, st)
        return 0

    if a.cmd == "task":
        p = scaffold.new_task(root, a.title, st)
        print(f"✅ 任务卡已生成: {p}")
        return 0

    if a.cmd == "check":
        r = gates.delivery_checklist(root, st)
        print("三审：" + " / ".join(r["three_reviews"]))
        print("三查：" + " / ".join(r["three_checks"]))
        print("必收准则：" + " / ".join(r["must_pass"]))
        print(f"人判点 {len(r['human_points'])} 个：" + "、".join(r["human_points"]))
        for n in r["notes"]:
            print("⚠️ " + n)
        if r["missing_files"]:
            for f in r["missing_files"]:
                print("❌ 缺文件: " + f)
            return 1
        print("✅ 骨架完整；以上条目需人工逐项确认后放行")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
