#!/usr/bin/env python3
"""Translation pass for the static builder.

English is the source. The generators keep emitting English markup; for every other language
`build.page()` runs that markup through a Translator, which swaps each block of copy for the
entry in build/i18n/<lang>.json and writes the page under /<lang>/.

A "unit" is the copy inside the lowest element that holds a sentence, with inline tags replaced
by numbered placeholders so the catalogue never contains markup:

    <p>Or <a href="…">start a project</a> without a call</p>
    ->  "Or <1>start a project</1> without a call"

Anything without an entry falls back to English and is listed in build/i18n/_missing.json.
Every unit the build saw is listed in build/i18n/_source.json (that is the file to translate from).
Mark copy that must never be translated (client names, verbatim reviews) with translate="no".
"""
import atexit, copy, html as _html, json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
CAT_DIR = HERE / "i18n"

# code: (name in its own language, og:locale, "this page is also available in …", button, dismiss)
LANGS = {
    "en": ("English", "en_US", "This page is also available in English.", "View in English", "Dismiss"),
    "de": ("Deutsch", "de_DE", "Diese Seite gibt es auch auf Deutsch.", "Auf Deutsch ansehen", "Schlie&#223;en"),
    "es": ("Espa&#241;ol", "es_ES", "Esta p&#225;gina tambi&#233;n est&#225; en espa&#241;ol.", "Ver en espa&#241;ol", "Cerrar"),
    "fr": ("Fran&#231;ais", "fr_FR", "Cette page existe aussi en fran&#231;ais.", "Voir en fran&#231;ais", "Fermer"),
    "nl": ("Nederlands", "nl_NL", "Deze pagina is er ook in het Nederlands.", "Bekijk in het Nederlands", "Sluiten"),
}
TARGETS = [l for l in LANGS if l != "en"]

# ───────────────────────── tiny HTML tree ─────────────────────────
_TAG = r'(?:"[^"]*"|\'[^\']*\'|[^\'">])'
TOKEN = re.compile(r'<!--.*?-->|<(script|style|svg)\b' + _TAG + r'*>.*?</\1\s*>|<' + _TAG + '+>', re.S)
VOID = {"br", "img", "input", "hr", "meta", "link", "source", "wbr", "area", "base", "col", "embed", "track"}
INLINE = {"a", "abbr", "b", "br", "cite", "code", "em", "i", "kbd", "mark", "q", "s", "small", "span",
          "strong", "sub", "sup", "time", "u", "wbr", "img"}
ATTRS = ("alt", "aria-label", "placeholder", "title", "data-cursor")
_ATTR = re.compile(r'(\s(?:' + "|".join(ATTRS) + r')=")([^"]*)(")')
_LETTER = re.compile(r"[^\W\d_]")
_WS = re.compile(r"\s+")
_PH = re.compile(r"<(/?)(\d+)(/?)>")


class El:
    __slots__ = ("name", "open", "close", "kids", "void", "done")

    def __init__(self, name, open_="", void=False):
        self.name, self.open, self.close, self.kids, self.void, self.done = name, open_, "", [], void, False


class Atom(str):
    """Markup that is copied through untouched (comments, scripts, SVG, translate="no")."""


def parse(src):
    root = El(None)
    stack, pos = [root], 0
    for m in TOKEN.finditer(src):
        if m.start() > pos:
            stack[-1].kids.append(src[pos:m.start()])
        tok, pos = m.group(0), m.end()
        if tok.startswith("<!") or m.group(1):
            stack[-1].kids.append(Atom(tok))
        elif tok.startswith("</"):
            name = tok[2:-1].strip().lower()
            for i in range(len(stack) - 1, 0, -1):
                if stack[i].name == name:
                    stack[i].close = tok
                    del stack[i:]
                    break
            else:
                stack[-1].kids.append(Atom(tok))
        else:
            name = re.match(r"<([a-zA-Z0-9-]+)", tok).group(1).lower()
            if name in VOID or tok.endswith("/>"):
                stack[-1].kids.append(El(name, tok, void=True))
            else:
                e = El(name, tok)
                stack[-1].kids.append(e)
                stack.append(e)
    if pos < len(src):
        stack[-1].kids.append(src[pos:])
    _freeze(root)
    return root


def ser(n):
    if isinstance(n, str):
        return n
    return n.open + "".join(ser(k) for k in n.kids) + n.close


def _freeze(e):
    """translate="no" subtrees become atoms."""
    for i, k in enumerate(e.kids):
        if isinstance(k, El):
            if 'translate="no"' in k.open:
                e.kids[i] = Atom(ser(k))
            else:
                _freeze(k)


def _letters(s):
    return bool(_LETTER.search(_html.unescape(s)))


def _has_text(n):
    if isinstance(n, Atom):
        return False
    if isinstance(n, str):
        return _letters(n)
    return any(_has_text(k) for k in n.kids)


def _phrasing(n):
    if isinstance(n, str):
        return True
    return n.name in INLINE and all(_phrasing(k) for k in n.kids)


def norm(s):
    """Catalogue form of a piece of source text: entities decoded, whitespace collapsed."""
    return _WS.sub(" ", _html.unescape(s)).strip()


# ───────────────────────── numbers ─────────────────────────
# The catalogues keep every number exactly as the English writes it (the checker enforces that, so a
# translation can never change a figure). The separators are swapped here, mechanically, because
# "2,237 hours" reads as two-and-a-bit hours to a German, Dutch, Spanish or French reader.
THOUSANDS = {"de": ".", "nl": ".", "es": ".", "fr": "\u202f"}      # fr: narrow no-break space
_GROUPED = re.compile(r"(?<![\d.,])\d{1,3}(?:,\d{3})+(?!\d|,\d)")
_DECIMAL = re.compile(r"(?<![\d.,])(\d+)\.(\d{1,2})(?![\d.])")


def locnum(s, lang):
    sep = THOUSANDS.get(lang)
    if not sep or not s:
        return s
    s = _DECIMAL.sub(lambda m: m.group(1) + "\x00" + m.group(2), s)
    s = _GROUPED.sub(lambda m: m.group(0).replace(",", sep), s)
    return s.replace("\x00", ",")


# Names that are the same in every language. Client names are added by build.py / pages3.py.
KEEP = {"Figma", "Webflow", "Framer", "GSAP", "n8n", "Zapier", "Make", "Lovable", "v0", "Cursor", "Claude Code",
        "Relume", "Finsweet", "LinkedIn", "Upwork", "Dribbble", "X", "CSS", "HTML", "JavaScript", "Anowar Hossain",
        "Anowar OS", "New York", "QA"}

# ───────────────────────── registry of everything seen ─────────────────────────
SOURCE = {}      # key -> {"kinds": set, "pages": set}
MISSING = {}     # lang -> {key: set(pages)}
_PAGES = set()


def _seen(key, kind, page):
    d = SOURCE.setdefault(key, {"kinds": set(), "pages": set()})
    d["kinds"].add(kind)
    d["pages"].add(page)
    _PAGES.add(page)


_CATS = {}


def catalogue(lang):
    if lang not in _CATS:
        f = CAT_DIR / f"{lang}.json"
        _CATS[lang] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    return _CATS[lang]


def plain(s):
    """A catalogue string with its placeholders removed (for JSON-LD and meta tags)."""
    return _WS.sub(" ", _PH.sub("", s)).strip()


class Translator:
    """lang=None is the English pass: it changes nothing but records every unit it meets."""

    def __init__(self, lang, page):
        self.lang, self.page = lang, page
        self.cat = catalogue(lang) if lang else None

    # ── lookups ──
    def _get(self, key, kind):
        if key in KEEP:
            return None
        if self.lang is None:
            _seen(key, kind, self.page)
            return None
        t = self.cat.get(key)
        if t is None:
            MISSING.setdefault(self.lang, {}).setdefault(key, set()).add(self.page)
        return t

    def text(self, s, kind="meta"):
        """A plain string that may hold entities (title, description). Returns escaped text."""
        if not s or not _letters(s):
            return s
        t = self._get(norm(s), kind)
        return locnum(s, self.lang) if t is None else _html.escape(locnum(plain(t), self.lang), quote=True)

    def raw(self, s, kind="js"):
        """Plain string in, plain string out (no escaping) — None when there is no translation."""
        t = self._get(norm(s), kind)
        return None if t is None else locnum(plain(t), self.lang)

    def fragment(self, s, kind="studio"):
        """An HTML string that is one unit (studio data, inline tags allowed). Returns HTML or None."""
        root = parse(s)
        out = self._run(root.kids, kind)
        return None if self.lang is None or out == s else out

    # ── markup ──
    def html(self, src):
        if not src:
            return src
        root = parse(src)
        self._walk(root)
        return src if self.lang is None else ser(root)

    def _attrs(self, e):
        def f(m):
            if not _letters(m.group(2)):
                return m.group(0)
            t = self._get(norm(m.group(2)), "attr")
            return m.group(0) if t is None else m.group(1) + _html.escape(locnum(plain(t), self.lang), quote=True) + m.group(3)
        if not e.done and e.open and '="' in e.open:
            e.open = _ATTR.sub(f, e.open)
        e.done = True

    def _walk(self, e):
        for k in e.kids:
            if isinstance(k, El):
                self._attrs(k)
        direct = any(isinstance(k, str) and not isinstance(k, Atom) and _letters(k) for k in e.kids)
        if direct:
            # split the children into runs of phrasing content; block children break a run
            out, run = [], []
            def flush():
                if run:
                    if any(_has_text(k) for k in run):
                        out.append(Atom(self._run(run, "text")))
                    else:
                        out.extend(run)
                    run.clear()
            for k in e.kids:
                if isinstance(k, Atom) or _phrasing(k):
                    run.append(k)
                else:
                    flush()
                    self._walk(k)
                    out.append(k)
            flush()
            e.kids = out
        else:
            for i, k in enumerate(e.kids):
                if isinstance(k, El):
                    self._walk(k)
                elif self.lang and not isinstance(k, Atom):
                    e.kids[i] = locnum(k, self.lang)

    def _run(self, kids, kind):
        """Translate one run of phrasing nodes; returns its markup."""
        parts = []            # ("t", text) | ("ph", raw) | ("o", raw) | ("c", raw)

        def emit(nodes):
            for k in nodes:
                if isinstance(k, Atom):
                    parts.append(("ph", str(k)))
                elif isinstance(k, str):
                    parts.append(("t", k))
                elif k.void or not _has_text(k):
                    self._attrs(k)
                    parts.append(("ph", ser(k)))
                else:
                    self._attrs(k)
                    parts.append(("o", k.open))
                    emit(k.kids)
                    parts.append(("c", k.close))
        emit(kids)
        original = "".join(locnum(p[1], self.lang) if p[0] == "t" else p[1] for p in parts)
        # peel off leading/trailing whitespace and placeholder-only markup (icons, arrows, ticks)
        a, b = 0, len(parts)
        while a < b and (parts[a][0] == "ph" or (parts[a][0] == "t" and not parts[a][1].strip())):
            a += 1
        while b > a and (parts[b - 1][0] == "ph" or (parts[b - 1][0] == "t" and not parts[b - 1][1].strip())):
            b -= 1
        core = parts[a:b]
        if not core:
            return original
        lead = "".join(p[1] for p in parts[:a])
        trail = "".join(p[1] for p in parts[b:])
        first, last = core[0], core[-1]
        if first[0] == "t" and first[1][:1].isspace():
            lead += " "
        if last[0] == "t" and last[1][-1:].isspace():
            trail = " " + trail
        key, tags, n, stack = [], {}, 0, []
        for kind_, val in core:
            if kind_ == "t":
                key.append(_html.unescape(val))
            elif kind_ == "ph":
                n += 1
                tags[f"<{n}/>"] = val
                key.append(f"<{n}/>")
            elif kind_ == "o":
                n += 1
                stack.append(n)
                tags[f"<{n}>"] = val
                key.append(f"<{n}>")
            else:
                m = stack.pop()
                tags[f"</{m}>"] = val
                key.append(f"</{m}>")
        key = _WS.sub(" ", "".join(key)).strip()
        if not _LETTER.search(_PH.sub("", key)):
            return original
        t = self._get(key, kind)
        if t is None:
            return original
        if sorted(_PH.findall(t)) != sorted(_PH.findall(key)):
            MISSING.setdefault(self.lang, {}).setdefault("BAD PLACEHOLDERS: " + key, set()).add(self.page)
            return original
        out, pos = [], 0
        for m in _PH.finditer(t):
            out.append(_html.escape(locnum(t[pos:m.start()], self.lang), quote=False))
            out.append(tags[m.group(0)])
            pos = m.end()
        out.append(_html.escape(locnum(t[pos:], self.lang), quote=False))
        return lead + "".join(out) + trail

    # ── JSON-LD ──
    _SCHEMA_KEYS = {"description", "text", "jobTitle", "serviceType", "headline"}
    _NAMED = {"Question", "ListItem", "Service", "Offer", "HowToStep", "HowTo", "OfferCatalog"}

    def schema(self, graph):
        g = copy.deepcopy(graph)
        self._schema(g)
        return g

    def _schema(self, o):
        if isinstance(o, list):
            for x in o:
                self._schema(x)
        elif isinstance(o, dict):
            if o.get("@type") == "Review":      # verbatim client reviews stay as written
                return
            for k, v in o.items():
                if isinstance(v, str):
                    if (k in self._SCHEMA_KEYS or (k == "name" and o.get("@type") in self._NAMED)) and _letters(v):
                        t = self._get(norm(v), "schema")
                        if t is not None:
                            o[k] = locnum(plain(t), self.lang)
                else:
                    self._schema(v)


# ───────────────────────── URLs ─────────────────────────
_NOT_PAGES = ("/assets", "/uploads", "/studio", "/api", "/_vercel")


def is_page(path):
    return path.startswith("/") and not path.startswith(_NOT_PAGES) and "." not in path.rsplit("/", 1)[-1]


def lpath(path, lang):
    """/pricing -> /de/pricing ; / -> /de ; English is unprefixed."""
    if not lang or lang == "en":
        return path
    return "/" + lang + ("" if path == "/" else path)


def localize_links(doc, lang):
    def f(m):
        return m.group(1) + lpath(m.group(2), lang) + m.group(3) if is_page(m.group(2)) else m.group(0)
    return re.sub(r'(\shref=")(/[^"#?]*)([^"]*")', f, doc)


# ───────────────────────── bookkeeping ─────────────────────────
def _flush():
    if not _PAGES:
        return
    CAT_DIR.mkdir(exist_ok=True)
    f = CAT_DIR / "_source.json"
    old = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    merged = {}
    for key, d in old.items():
        pages = [p for p in d["pages"] if p not in _PAGES]
        if pages:
            merged[key] = {"kinds": set(d["kinds"]), "pages": set(pages)}
    for key, d in SOURCE.items():
        m = merged.setdefault(key, {"kinds": set(), "pages": set()})
        m["kinds"] |= d["kinds"]
        m["pages"] |= d["pages"]
    # document order (not alphabetical), so neighbouring entries share their context
    out = {k: {"kinds": sorted(v["kinds"]), "pages": sorted(v["pages"])} for k, v in merged.items()}
    f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    mf = CAT_DIR / "_missing.json"
    miss = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {}
    for lang in TARGETS:
        kept = {k: [p for p in v if p not in _PAGES] for k, v in miss.get(lang, {}).items()}
        kept = {k: v for k, v in kept.items() if v}
        for k, pages in MISSING.get(lang, {}).items():
            kept[k] = sorted(set(kept.get(k, [])) | pages)
        miss[lang] = dict(sorted(kept.items()))
    mf.write_text(json.dumps(miss, ensure_ascii=False, indent=1), encoding="utf-8")
    n = {l: len(miss[l]) for l in TARGETS if miss[l]}
    if n:
        print("  i18n: untranslated units ->", n, "(build/i18n/_missing.json)")


atexit.register(_flush)
