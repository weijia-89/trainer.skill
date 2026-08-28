#!/usr/bin/env python3
import json, os, re, sys, math, stat, unicodedata, subprocess
from pathlib import Path
from collections import defaultdict

# Strip zero-width / directional-override characters that evade prompt-injection
# and secret matchers, then NFKC-normalize so confusable glyphs collapse to the
# canonical form before scanning (C9 / C2 evasion hardening).
_ZW = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\u2061\u2062\u2063\u2064\ufeff\u202a\u202b\u202c\u202d\u202e"))
def norm_text(s):
    return unicodedata.normalize("NFKC", s.translate(_ZW))
ROOT = Path(os.path.expanduser(os.environ.get("SKILL_TREE_ROOT", "~/.config/opencode/skills")))
OUT = Path(os.path.expanduser(os.environ.get("SKILL_TREE_OUT", str(Path(__file__).resolve().parent / "findings-skill-tree.json"))))
if not ROOT.is_dir():
    print(f"ERROR: LOOP1_ROOT is not a directory: {ROOT}", file=sys.stderr)
    sys.exit(2)
findings = []
def add(pid, sev, skill, path, line, desc, falsifier):
    findings.append({"id": pid, "sev": sev, "skill": skill, "path": str(path), "line": line, "finding": desc, "falsifier": falsifier})

# Redact secret material from any text that gets echoed into a finding (ctx,
# matched snippet, URL). Only C1 was redacted before; C2/C5/C6/C7 embed raw
# file context that can carry a secret adjacent to the matched pattern, so the
# secret would otherwise land in cleartext in findings-loop1.json + stdout.
_KV_RE = re.compile(r"(?i)(token|secret|password|passwd|api[_-]?key|access[_-]?key|private[_-]?key|auth(?:orization)?)\s*[=:]\s*\S+")
_AUTH_RE = re.compile(r"(?i)\b(Bearer|Basic)\s+[A-Za-z0-9._~+/\-]+=*")
def redact(s):
    if s is None:
        return s
    for pat, _label, _ in SECRET_PATTERNS:
        s = re.sub(pat, "<REDACTED-SECRET>", s)
    s = _AUTH_RE.sub(r"\1 <REDACTED>", s)
    return _KV_RE.sub(r"\1=<REDACTED>", s)

SECRET_ALLOWLIST = {"AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI"}
SECRET_PATTERNS = [
    (r"gh[posu]_[A-Za-z0-9]{20,}", "GitHub token", False),
    (r"sk-(ant-)?[A-Za-z0-9_-]{25,}", "Anthropic/OpenAI-style key", True),
    (r"AKIA[0-9A-Z]{16}", "AWS access key", False),
    (r"BEGIN [A-Z ]*PRIVATE KEY", "private key block", False),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "Slack token", False),
    (r"npm_[A-Za-z0-9]{30,}", "npm token", False),
    (r"gsk_[A-Za-z0-9_]{20,}", "Groq key", False),
]
EGRESS_PATTERNS = [
    (r"\b(curl|wget|nc|netcat)\b[^|]*\|\s*(ba)?sh", "curl/wget piped to shell"),
    (r"(?:https?|ftps?)://(?!(127\.0\.0\.1(?=/|:|$)|localhost(?=/|:|$)|registry\.npmjs\.org(?=/|:|$)|raw\.githubusercontent\.com/(?:ayghri|i-have-adhd)(?=/|:|$)|github\.com(?=/|:|$)|api\.github\.com(?=/|:|$)|opencode\.ai(?=/|:|$)|json-schema\.org(?=/|:|$)|json\.schemastore\.org(?=/|:|$)|playwright\.dev(?=/|:|$)|code\.visualstudio\.com(?=/|:|$)|developer\.mozilla\.org(?=/|:|$)|doi\.org(?=/|:|$)|example\.com(?=/|:|$)|www\.w3\.org(?=/|:|$)|www\.idpf\.org(?=/|$)|www\.daisy\.org(?=/|$)|norvig\.com(?=/|$)))(?:[\w.-]+\.[\w.-]+)", "non-allowlisted absolute URL"),
    (r"(?<![:/])//[A-Za-z0-9.-]+\.[A-Za-z0-9.-]+", "protocol-relative (scheme-less) URL"),
    (r"/dev/(tcp|udp)/\d", "reverse-shell / exfil channel (/dev/tcp|udp)"),
    (r"nc\s+\S+\s+-e\s+\S+", "reverse-shell / exfil channel (nc -e)"),
    (r"bash\s+-i\b", "reverse-shell / exfil channel (bash -i)"),
    (r"\b(fetch|axios\.(get|post)|requests\.(get|post)|urllib\.request|http\.client)\b", "programmatic HTTP call"),
    (r"(telemetry|analytics|beacon|track_event|umami|posthog|mixpanel|segment\.io|sentry\.io)", "telemetry indicator"),
]
EXEC_PATTERNS = [
    (r"\beval\s*\(|\bexec\s*\(|os\.system\s*\(|subprocess.*shell\s*=\s*True|new Function\s*\(", "dynamic execution"),
    (r"base64(-D|--decode|-d)\b.*\|\s*(ba)?sh|frombase64string|atob\s*\(", "base64-decoded execution"),
]
PERSIST_PATTERNS = [
    (r"crontab\b|launchctl\b|LaunchAgents|~/\.zshrc|~/\.zprofile|~/\.bashrc|chflags\s|defaults\s+write\s+com\.apple", "persistence mechanism"),
]
CRED_PATTERNS = [
    (r"~/?\.ssh|~/?\.aws|security\s+(list-keychains|find-generic-password|find-internet-password|unlock-keychain)|keychain|Cookies\s|Login Data|\.netrc", "credential store access"),
]

# Supply-chain: a skill script that pulls/fetches/clones/pushes from a remote can
# mutate its own (or the repo's) source at runtime -> remote code-change risk.
GIT_NET_RE = re.compile(r"\bgit\s+(pull|fetch|clone|push)\b")

# Sensitive files that must never be shipped inside a skill bundle (C2 egress to
# Manus would expose them). Defensive: currently zero hits in the tree.
SENSITIVE_FILES = {".env", ".env.local", ".envrc", "id_rsa", "id_dsa", "id_ecdsa",
                    "id_ed25519", "id_ed448", "id_xmss", "id_ecdsa_sk", "id_ed25519_sk",
                    "credentials.json", ".netrc", "token.json", "secrets.json"}
SENSITIVE_SUFFIX = (".pem", ".key", ".p12", ".pkcs12", ".age", ".kdbx", ".gpg",
                    ".pfx", ".jks", ".keystore", ".der", ".priv")

CODE_SUFFIXES = {".sh", ".py", ".js", ".mjs", ".cjs", ".ts"}

def walk():
    for p in sorted(ROOT.rglob("*")):
        if ".git" in p.parts or "node_modules" in p.parts or "__pycache__" in p.parts:
            continue
        yield p

def frontmatter(text):
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else None

skills = {}
allfiles = [p for p in walk() if p.is_file()]

for p in allfiles:
    rel = p.relative_to(ROOT)
    skill = rel.parts[0] if len(rel.parts) > 1 else "(root)"
    try:
        text = norm_text(p.read_text(encoding="utf-8"))
        enc_ok = True
    except UnicodeDecodeError:
        enc_ok = False
        text = ""
        add("S11", "P3", skill, rel, 0, "File is not valid UTF-8 (or is binary) inside an md-based skill tree", f"file $(file -b {p}) shows non-text")
    if not enc_ok:
        continue

    if p.name == "SKILL.md":
        fm = frontmatter(text)
        parent = p.parent.name
        if fm is None:
            add("S1", "P2", skill, rel, 1, "SKILL.md missing well-formed --- frontmatter block", f"head -3 {p}")
        else:
            nm = re.search(r"^name:\s*(\S+)", fm, re.M)
            de = re.search(r"^description:", fm, re.M)
            if not nm:
                add("S1", "P2", skill, rel, 1, "frontmatter missing name:", f"grep -c '^name:' {p}")
            else:
                name = nm.group(1).strip().strip('\'"')
                skills.setdefault(name, []).append(str(rel))
                if name != parent:
                    add("S2", "P2", skill, rel, 0, f"folder/skill-name mismatch: folder={parent} name={name}", "ls dir; grep ^name: SKILL.md")
                if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
                    add("S2", "P3", skill, rel, 0, f"name violates lowercase-hyphen convention: {name}", "grep ^name:")
                if len(name) > 64:
                    add("S2", "P4", skill, rel, 0, f"name exceeds 64 chars", "wc -c")
            if not de:
                add("S3", "P2", skill, rel, 1, "frontmatter missing description: (skill never surfaced to model)", "grep -c '^description:' SKILL.md")
            else:
                dm = re.search(r"description:\s*(>.*)?(\||>[-+]?)?\s*\n?((?:[ \t]+.*)|\S.*)?", fm, re.S)
                dlen = len(fm.split("description:",1)[1]) if "description:" in fm else 0
                if dlen > 1600:
                    add("A8", "P3", skill, rel, 0, f"description very long (~{dlen} chars); billed into system context every session across all 54 skills", "awk frontmatter length")

    low = text.lower()
    lines = text.split("\n")
    for pat, label, need_digit in SECRET_PATTERNS:
        for m in re.finditer(pat, text):
            if any(a in m.group(0) for a in SECRET_ALLOWLIST):
                continue
            if need_digit and not any(c.isdigit() for c in m.group(0)):
                continue
            add("C1", "P1" if "PRIVATE KEY" not in label else "P0", skill, rel, text[:m.start()].count("\n")+1, f"potential secret ({label}): <redacted, {len(m.group(0))} chars>", f"grep -nE '{pat}' {p}")
    is_code = p.suffix in CODE_SUFFIXES
    for pat, label in EGRESS_PATTERNS:
        for m in re.finditer(pat, text, re.I):
            ctx = redact(text[max(0,m.start()-60):m.end()+60].replace("\n"," "))
            if label == "programmatic HTTP call" and ("mock" in ctx.lower() or "127.0.0.1" in ctx): continue
            if label == "non-allowlisted absolute URL":
                line = lines[text[:m.start()].count("\n")]
                if re.search(r"\]\([^)]*" + re.escape(m.group(0).split('?')[0][:20]), line) and not is_code:
                    add("C2", "P4", skill, rel, text[:m.start()].count("\n")+1, f"doc-citation link (not runtime egress): {redact(m.group(0))[:60]}", f"grep -n '{m.group(0)[:40]}' {p}")
                    continue
            sev = "P2" if is_code else "P4"
            tag = "" if is_code else " (doc prose)"
            add("C2", sev, skill, rel, text[:m.start()].count("\n")+1, f"{label}{tag}: …{ctx[:120]}…", f"grep -niE '{pat}' {p}")
    for pat, label in EXEC_PATTERNS:
        for m in re.finditer(pat, text, re.I):
            add("C5", "P2" if is_code else "P4", skill, rel, text[:m.start()].count("\n")+1, f"{label}{'' if is_code else ' (doc prose)'}: {redact(m.group(0))[:40]}", f"grep -nE '{pat}' {p}")
    for pat, label in PERSIST_PATTERNS:
        for m in re.finditer(pat, text, re.I):
            add("C6", "P2" if is_code else "P4", skill, rel, text[:m.start()].count("\n")+1, f"{label}{'' if is_code else ' (doc prose)'}: {redact(m.group(0))[:40]}", f"grep -nE '{pat}' {p}")
    for pat, label in CRED_PATTERNS:
        for m in re.finditer(pat, text, re.I):
            ctx = redact(text[max(0,m.start()-50):m.end()+50].replace("\n"," "))
            if "example" in ctx.lower() or "list-keychains" in ctx or not is_code: sev="P4"
            else: sev="P2"
            add("C7", sev, skill, rel, text[:m.start()].count("\n")+1, f"{label}{'' if is_code else ' (doc prose)'}: …{ctx[:110]}…", f"grep -nE '{pat}' {p}")
    # Supply-chain: network git op inside an executable skill script (C11).
    if is_code:
        for m in GIT_NET_RE.finditer(text):
            add("C11", "P2", skill, rel, text[:m.start()].count("\n")+1,
                f"network git op in script ({m.group(0)}): can mutate sources at runtime",
                f"grep -nE 'git (pull|fetch|clone|push)' {p}")

for name, locs in sorted(skills.items()):
    if len(locs) > 1:
        add("S8", "P2", name, ";".join(locs), 0, f"duplicate skill name registered {len(locs)}x → loader collision", "python3 tools/loop1_scan.py | grep S8")

for p in walk():
    rel = p.relative_to(ROOT)
    if p.is_symlink():
        tgt = os.readlink(p)
        if not os.path.exists(p):
            add("S12", "P2", rel.parts[0], rel, 0, f"dangling symlink -> {tgt}", f"readlink {p}")
        elif not os.path.realpath(p).startswith(str(ROOT)):
            add("S12", "P2", rel.parts[0], rel, 0, f"symlink escapes skills tree -> {os.path.realpath(p)}", f"realpath {p}")
    if p.is_file() and ".git" not in p.parts:
        mode = p.stat().st_mode
        if mode & stat.S_IWOTH:
            add("C8", "P3", rel.parts[0], rel, 0, "world-writable file", f"ls -l {p}")
        if mode & (stat.S_ISUID | stat.S_ISGID):
            add("C8", "P2", rel.parts[0], rel, 0, "setuid/setgid file", f"ls -l {p}")

for d in ROOT.rglob("*"):
    if d.is_dir() and (d.name in {"node_modules","__pycache__",".git"} or d.name == ".DS_Store"):
        add("S5", "P3", d.relative_to(ROOT).parts[0], d.relative_to(ROOT), 0, f"build/VCS artifact directory installed: {d.name}/", f"du -sh {d}")

# S13: sensitive files that must never ship inside a skill bundle.
for p in walk():
    if not p.is_file():
        continue
    nm = p.name
    if nm in SENSITIVE_FILES or nm.startswith(".env") or nm.endswith(SENSITIVE_SUFFIX):
        rel = p.relative_to(ROOT)
        add("S13", "P2", rel.parts[0], rel, 0, f"sensitive file present in skill tree: {nm}", f"file {p}")

mdlinks = re.compile(r"\[[^\]]*\]\((?!https?://|#|mailto:)([^)#]+)")
FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"`[^`\n]*`")

# Prompt-injection / instruction-override surface (Posture 2/4, Loop 2).
# NOTE: the specifier prefix is a SINGLE token class `[a-z]+ ` inside the `*`
# (NOT an alternation of space-words) to keep matching linear and avoid ReDoS
# on long repeated-token lines. See tests/test_scanner.py::test_injection_redos.
INJECT_RE = re.compile(
    r"ignore (?:[a-z]+ )*(instructions|prompt|system message|system prompt)"
    r"|disregard (?:[a-z]+ )*(instructions|prompt|system message|system prompt)"
    r"|you are (?:now )?(?:in|operating in) (?:developer|debug|admin|root|privileged) mode"
    r"|system prompt:|DAN mode|developer mode|jailbreak",
    re.I,
)

def _masked_lines(text):
    # Yield (line_no, line) with fenced blocks and inline-code spans blanked,
    # so S4 judges real prose links only (red-green fixture-validated 2026-08-25).
    open_marker = None
    for i, line in enumerate(text.splitlines(), 1):
        fm = FENCE_OPEN.match(line)
        if fm:
            run = fm.group(1)
            if open_marker is None:
                open_marker = run[0] * len(run)
            elif run[0] == open_marker[0] and len(run) >= len(open_marker):
                open_marker = None
            yield (i, "")
            continue
        yield (i, "" if open_marker else INLINE_CODE.sub("", line))

for p in allfiles:
    if p.suffix != ".md": continue
    try: text = norm_text(p.read_text(errors="ignore"))
    except Exception: continue
    skill = p.relative_to(ROOT).parts[0]
    for ln, line in _masked_lines(text):
        for m in mdlinks.finditer(line):
            tgt = m.group(1).strip()
            if tgt.startswith("<"): tgt = tgt[1:]
            if any(c in tgt for c in "{}^$<>| ") or tgt.startswith(("computer://", "file://")) or tgt in ("...", "path", "url", "link", "badge"):
                continue
            resolved = (p.parent / tgt).resolve()
            if not resolved.exists():
                add("S4", "P2", skill, p.relative_to(ROOT), ln, f"broken relative link: ({tgt})", f"test -e {resolved} || echo MISSING")

# Prompt-injection sweep:
#  - prose (.md): scanned here (comprehensive INJECT_RE), AND form-check's
#    canonical scan_prompt_injection.sh is run as a second opinion (its regex is
#    stricter, so running both maximizes recall — neither is dropped).
#  - code (.py/.sh/.js/...): scanned here only — form-check's bash scanner
#    covers *.md, so code injection is the genuine gap the standing audit fills.
_seen = set()
for p in allfiles:
    skill = p.relative_to(ROOT).parts[0]
    if p.suffix == ".md":
        for ln, line in _masked_lines(p.read_text(errors="ignore")):
            for m in INJECT_RE.finditer(norm_text(line)):
                _seen.add((str(p.relative_to(ROOT)), ln))
                add("C9", "P3", skill, p.relative_to(ROOT), ln,
                    f"possible prompt-injection ({m.group(0)[:40]})", f"grep -niE 'ignore|disregard|system prompt' {p}")
    elif p.suffix in CODE_SUFFIXES:
        code_text = norm_text(p.read_text(errors="ignore"))
        for m in INJECT_RE.finditer(code_text):
            add("C9", "P2", skill, p.relative_to(ROOT),
                code_text[:m.start()].count("\n") + 1,
                f"possible prompt-injection in code ({m.group(0)[:40]})", f"grep -niE 'ignore|disregard|system prompt' {p}")
# Second-opinion prose scan via form-check (adds signal not caught above).
_bash_scan = Path(__file__).resolve().parent / "scan_prompt_injection.sh"
try:
    res = subprocess.run([str(_bash_scan), str(ROOT)], capture_output=True, text=True)
    for hl in res.stdout.splitlines():
        mm = re.match(r"^(.+?):(\d+):\s*(.*)$", hl)
        if not mm:
            continue
        fp = Path(mm.group(1))
        rel = fp.relative_to(ROOT) if fp.is_relative_to(ROOT) else fp
        key = (str(rel), int(mm.group(2)))
        if key in _seen:
            continue
        add("C9", "P3", rel.parts[0], rel, int(mm.group(2)),
            f"possible prompt-injection (prose, form-check scan): {mm.group(3)[:60]}",
            f"grep -niE 'ignore|disregard|system prompt' {fp}")
except Exception as e:
    print(f"WARN: prose injection second-opinion scan failed: {e}", file=sys.stderr)

total_desc_bytes = sum(len(frontmatter(p.read_text(errors='ignore')).split('description:',1)[-1]) for p in allfiles if p.name=="SKILL.md" and frontmatter(p.read_text(errors='ignore')))
add("A12", "P4", "(tree)", "(aggregate)", 0, f"context budget: ~{len(skills)} skills advertised; description payload ≈{total_desc_bytes//1024}KB (~{total_desc_bytes//4//1024}Ktok) loaded every session", "cat */SKILL.md | wc -c")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(findings, indent=1, ensure_ascii=False), encoding="utf-8")
sev_order = {"P0":0,"P1":1,"P2":2,"P3":3,"P4":4}
for f in sorted(findings, key=lambda x: sev_order[x["sev"]]):
    print(f'{f["sev"]}\t{f["id"]}\t{f["skill"]}\t{f["path"]}:{f["line"]}\t{f["finding"][:150]}')
print(f"\nTOTAL={len(findings)}", file=sys.stderr)
