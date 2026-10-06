#!/usr/bin/env python3
"""一致性校验：所有客户端版本的规则集必须完全相同，元信息必须齐全。

用法: python3 tools/check.py
退出码 0 = 通过，1 = 失败。
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
errors = []


def err(msg):
    errors.append(msg)


# ── 文件发现 ────────────────────────────────────────────────
def egern_files():
    return sorted(p for p in (ROOT / "egern").glob("*.yaml")
                  if not p.name.startswith("snippet"))


def text_files():
    return sorted((ROOT / "surge").glob("*.sgmodule")) + \
        sorted((ROOT / "loon").glob("*.plugin"))


def is_plus(path):
    return "plus" in path.name


# ── 规则提取 ────────────────────────────────────────────────
def rules_from_egern(path):
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        err(f"{path.relative_to(ROOT)}: YAML 解析失败 — {exc}")
        return None, None
    out = set()
    for rule in doc.get("rules", []):
        for kind in ("domain", "domain_suffix", "domain_keyword", "domain_regex"):
            if kind in rule:
                out.add((kind, rule[kind]["match"]))
    return out, doc


RULE_RE = re.compile(r"^DOMAIN(-SUFFIX|-KEYWORD|-REGEX)?,([^,]+),REJECT", re.M)
KIND = {"": "domain", "-SUFFIX": "domain_suffix",
        "-KEYWORD": "domain_keyword", "-REGEX": "domain_regex"}


def rules_from_text(path):
    text = path.read_text(encoding="utf-8")
    live = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    out = {(KIND.get(suffix, "domain"), domain.strip())
           for suffix, domain in RULE_RE.findall(live)}
    return out, text


# ── 校验 ────────────────────────────────────────────────────
REQUIRED_META = ["name", "desc", "author", "icon", "homepage"]

baseline, baseline_name = None, None
plus_features = {}


def compare(path, rules):
    global baseline, baseline_name
    if baseline is None:
        baseline, baseline_name = rules, str(path.relative_to(ROOT))
    elif rules != baseline:
        err(f"{path.relative_to(ROOT)}: 规则集与 {baseline_name} 不一致 "
            f"(多出 {sorted(rules - baseline)}, 缺少 {sorted(baseline - rules)})")


for path in egern_files():
    rules, doc = rules_from_egern(path)
    if rules is None:
        continue
    for field in ("name", "description", "author", "homepage", "icon"):
        if not doc.get(field):
            err(f"{path.relative_to(ROOT)}: 缺少元信息字段 {field}")
    compare(path, rules)

    rel = str(path.relative_to(ROOT))
    if is_plus(path):
        features = {k for k in ("map_locals", "url_rewrites", "mitm") if doc.get(k)}
        plus_features.setdefault("egern", set()).update(features)
        for key in ("map_locals", "mitm"):
            if not doc.get(key):
                err(f"{rel}: 进阶版缺少 {key}")
    else:
        if doc.get("mitm") or doc.get("url_rewrites"):
            err(f"{rel}: 基础版不应包含 mitm / url_rewrites")

for path in text_files():
    rules, text = rules_from_text(path)
    rel = str(path.relative_to(ROOT))
    for field in REQUIRED_META:
        if not re.search(rf"^#!\s*{field}\s*=", text, re.M):
            err(f"{rel}: 缺少元信息头 #!{field}=")
    compare(path, rules)

    if is_plus(path):
        # 只看生效行，注释掉的段不算（基础版/进阶版都会把可选段注释掉）
        live = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
        section_to_key = {"[Map Local]": "map_locals",
                          "[URL Rewrite]": "url_rewrites",
                          "[MITM]": "mitm"}
        features = {key for section, key in section_to_key.items()
                    if section in live}
        plus_features.setdefault("text", set()).update(features)
        for section in ("[Map Local]", "[MITM]"):
            if section not in live:
                err(f"{rel}: 进阶版缺少 {section}")
    else:
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                continue
            if re.match(r"^mitm\s*:", line) or line.strip() in ("[MITM]", "[Mitm]"):
                err(f"{rel}: 基础版不应包含 MITM 段")

# ── 进阶版：Egern 与 Surge 的改写能力必须一一对应 ───────────
if plus_features.get("egern") != plus_features.get("text"):
    err("进阶版的改写能力在 Egern 与 Surge 之间不一致: "
        f"egern={sorted(plus_features.get('egern', []))} "
        f"surge={sorted(plus_features.get('text', []))}")

# ── 其它资源 ────────────────────────────────────────────────
for extra in ("icon.png", "README.md", "LICENSE"):
    if not (ROOT / extra).exists():
        err(f"{extra}: 文件不存在")

# ── 结果 ────────────────────────────────────────────────────
if errors:
    for e in errors:
        print(f"FAIL  {e}")
    print(f"\n✗ {len(errors)} 项失败")
    sys.exit(1)

count = len(baseline) if baseline else 0
print(f"✓ 全部通过 — {count} 条规则，{len(egern_files()) + len(text_files())} 份配置一致")
