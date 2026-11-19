#!/usr/bin/env python3
"""Working with the translation catalogues (build/i18n/<lang>.json).

  python i18n_tool.py export [lang]   write what still needs translating to build/i18n/_work/src.NN.json
                                      (everything when no language is given)
  python i18n_tool.py check <lang>    validate build/i18n/_work/<lang>.NN.json against the source chunks
  python i18n_tool.py merge <lang>    check, then fold the chunks into build/i18n/<lang>.json
  python i18n_tool.py status          per language: translated, missing, and stale entries
  python i18n_tool.py prune <lang>    drop catalogue entries the site no longer uses

A source chunk is a list of {"id", "en", "kind", "page"}; a translated chunk is {"<id>": "translation"}.
Run the three page builders first so _source.json is current.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
CAT = HERE / "i18n"
WORK = CAT / "_work"
CHUNK = 120
PH = re.compile(r"<(/?)(\d+)(/?)>")
NUM = re.compile(r"\d+(?:[.,:]\d+)*")


def load(name, default=None):
    f = CAT / name
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else ({} if default is None else default)


def problems(en, tr):
    out = []
    if not isinstance(tr, str) or not tr.strip():
        return ["empty"]
    if sorted(PH.findall(en)) != sorted(PH.findall(tr)):
        out.append(f"placeholders differ: {sorted(m.group(0) for m in PH.finditer(en))} vs {sorted(m.group(0) for m in PH.finditer(tr))}")
    strip = lambda s: PH.sub(" ", s)
    a, b = sorted(NUM.findall(strip(en))), sorted(NUM.findall(strip(tr)))
    if a != b:
        out.append(f"numbers differ: {a} vs {b}")
    if re.search(r"&(?:[a-z]+|#\d+);", tr):
        out.append("HTML entity in the translation (write the character itself)")
    if re.search(r"<(?!/?\d+/?>)", tr):
        out.append("stray '<' (only <1>, </1>, <2/> style placeholders are allowed)")
    if tr != tr.strip() or "\n" in tr:
        out.append("leading/trailing space or line break")
    plain_en, plain_tr = strip(en).strip(), strip(tr).strip()
    if len(plain_en) <= 24 and len(plain_tr) > max(len(plain_en) * 2.2, len(plain_en) + 14):
        out.append(f"long for a short label ({len(plain_tr)} vs {len(plain_en)} characters)")
    return out


def chunks():
    return sorted(WORK.glob("src.*.json"))


def read_work(lang):
    src, tr = {}, {}
    for f in chunks():
        for u in json.loads(f.read_text(encoding="utf-8")):
            src[str(u["id"])] = u
        g = WORK / f.name.replace("src.", lang + ".")
        if g.exists():
            tr.update({str(k): v for k, v in json.loads(g.read_text(encoding="utf-8")).items()})
    return src, tr


def check(lang, quiet=False):
    src, tr = read_work(lang)
    bad = 0
    for i, u in src.items():
        if i not in tr:
            bad += 1
            print(f"[{i}] missing: {u['en'][:70]}")
            continue
        for p in problems(u["en"], tr[i]):
            bad += 1
            print(f"[{i}] {p}\n      en: {u['en'][:160]}\n      {lang}: {tr[i][:160]}")
    extra = set(tr) - set(src)
    if extra:
        bad += 1
        print("unknown ids:", sorted(extra)[:20])
    if not quiet or bad:
        print(f"{lang}: {len(src)} units, {len([i for i in src if i in tr])} translated, {bad} problems")
    return bad


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    lang = sys.argv[2] if len(sys.argv) > 2 else None
    source = load("_source.json")
    if cmd == "export":
        have = load(f"{lang}.json") if lang else {}
        todo = [(k, v) for k, v in source.items() if k not in have]
        WORK.mkdir(parents=True, exist_ok=True)
        for f in WORK.glob("src.*.json"):
            f.unlink()
        units = [{"id": i + 1, "en": k, "kind": "/".join(v["kinds"]), "page": min(v["pages"], key=lambda p: (p.startswith("("), len(p)))} for i, (k, v) in enumerate(todo)]
        for n in range(0, len(units), CHUNK):
            (WORK / f"src.{n // CHUNK + 1:02d}.json").write_text(json.dumps(units[n:n + CHUNK], ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{len(units)} units in {len(chunks())} chunks -> {WORK}")
    elif cmd == "check":
        sys.exit(1 if check(lang) else 0)
    elif cmd == "merge":
        if check(lang, quiet=True):
            sys.exit("fix the problems above first")
        src, tr = read_work(lang)
        cat = load(f"{lang}.json")
        cat.update({src[i]["en"]: tr[i] for i in src})
        (CAT / f"{lang}.json").write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{lang}.json: {len(cat)} entries")
    elif cmd == "prune":
        cat = load(f"{lang}.json")
        kept = {k: v for k, v in cat.items() if k in source}
        (CAT / f"{lang}.json").write_text(json.dumps(kept, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{lang}.json: dropped {len(cat) - len(kept)}, kept {len(kept)}")
    else:
        for f in sorted(CAT.glob("??.json")):
            cat = json.loads(f.read_text(encoding="utf-8"))
            bad = sum(1 for k, v in cat.items() if k in source and problems(k, v))
            print(f"{f.stem}: {sum(1 for k in source if k in cat)}/{len(source)} translated, "
                  f"{sum(1 for k in source if k not in cat)} missing, {sum(1 for k in cat if k not in source)} stale, {bad} with problems")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
