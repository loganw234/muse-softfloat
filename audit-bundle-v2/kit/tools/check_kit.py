#!/usr/bin/env python3
"""The kit's gate. Run it first, on day 1, before reading anything else in the kit.

    python3 -I tools/check_kit.py [KIT_DIR]            the five checks; exit 0 only if every one holds
    python3 -I tools/check_kit.py --control [KIT_DIR]  plant one fault for each finding the checks can give, each in a
                                                      fresh copy, and exit 0 only if each plant is caught by its own
                                                      check, by the finding that names it; then spell each privacy
                                                      shape with each letter `re` folds, and require each spelling
                                                      to be found

KIT_DIR defaults to the directory above this file. Exit 1 is a refusal, with a line for each, naming the file and
what was found. Exit 2 is bad usage, or git missing: a gate that cannot read the bundle does not pass it. Exit 3 is the
gate itself failing, which is no verdict either way. A bundle that git cannot read is a finding of checks 2 and 4,
which cannot look inside it.

The checks (docs/KIT-0.md section 8, in the builder's repository; this kit's START-HERE.md says what they are for):
1. manifest   every file's sha256 matches MANIFEST.txt, which names its sources; no file is extra or missing; no PDF
              anywhere, archives and the QRO-Crate bundle included (the IEEE 754 standard is Logan's, under his
              licence, and stays out). This shows that the kit matches its own manifest. What shows that it is the
              kit that was built is the zip's sha256, which Logan holds.
2. links      every relative link in a Markdown file the kit carries as a file resolves inside the kit. No URL, in any
              file, archive member, bundle blob or commit message, leads to the repository this kit keeps you away
              from, in the forms CFT_FORMS lists: its pages on github.com and any fork's, git's scp-like remote form,
              and the API, raw and Pages hosts. Backslashes are dropped, and percent-encoding undone, first. Not
              matched: a mirror on another host, a fork under another name, a copy shown through another repository
              (a submodule's view), an HTML-entity spelling, and a URL split across lines. The clean room's rule and
              disclosure cover those. Relative links inside an archive member or the bundle are the record's,
              written from their own repository's root, and are not resolved.
3. terms      no line of the files the builder wrote from that repository's record holds a term of TERMS below.
              This is a stated limit, not a guarantee: a list catches a line that names a listed term and cannot see
              the same thing said in other words. The builder read every such file whole as well.
4. privacy    no home path with a name, no email address but the kept ones, no key or token of the shapes below, no
              private-range IPv4 address, no user@host that names Logan's user name or his desktop's name, not his
              desktop's name, and neither of the fragments FRAGMENTS holds. The one exception is the QRO-Crate bundle's
              commit identities, which carry his address by his word (2026-10-23: "Real address is fine"). What it
              does not refuse, by the plan: his site's domain as text (the builder's rule R6), and the names of his
              Linux machine and his WSL distro, which his published texts spell (the builder's KIT-0.md, section 13).
5. generated  START-HERE.md's reading table and examples/README.md's sample table match what they describe.

Names that must not appear are held here by sha256 only, so the gate never spells them. The controls cannot spell
them either, so check 4's name matching is controlled with control names whose hashes are added in --control mode
only; the builder's own tests run the same check on the unredacted archives, where the real names are, and see it
refuse them.

Stdlib only. Shapes for paths, addresses and keys follow QRO-Crate's tools/check_privacy.py (ALTERNATIVES), which
this kit carries in reference/QRO-Crate.bundle.
"""
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import zipfile
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def cat(*parts):
    """A string built at run time from its parts. The controls' samples are built this way, so that no file of the
    kit holds one whole, not even a .pyc, where the compiler would join "a" + "b" into one constant."""
    return "".join(parts)


# ---- names, by sha256 ----
# Logan's user name.
USER_NAMES = {"5ba4c5ad7f67ea1a40f3108d9af56d063ec36d3400d810573769eb5c07809af8"}
# His desktop's name, as written and lower-cased. The names of his Linux machine and his WSL distro are not here:
# his published texts spell them, and the kit carries those texts (the builder's KIT-0.md, section 13).
MACHINE_NAMES = {"65603b74806ba3d86a78df14b13a8939cf1fc264ab48a483ccc79ee26a2d7f4d",
                 "82906b8e03668276bdc23cc57f7d09214b3cc677dd52014284be9c78213f1b8e"}
# His personal domains: his email's, and his site's. An address at either is refused. His site's domain is carried as
# text, by the plan (R6).
PERSONAL_DOMAINS = {"0c6e258fbe0837f27541c44a2744d0a0a2a8d2047a281c04fcc056c4aeb7f3cc",
                    "bffdbab0ec88b496cf1eff8ed473f970e39bc76a64f9cdd32eaef0bc14981e92"}
# Two fragments, refused wherever they stand alone: his email domain's name without its top-level domain, and the
# prefix of an account id that round 4's privacy sweep searched for.
F_LABEL = "the name of Logan's email domain"
F_PREFIX = "the prefix of Logan's account id"
FRAGMENTS = {"f194464dece630691241a0270e087d6aee20c322189961eab131f4ba3be7d51c": F_LABEL,
             "293e24c76cdfb8afba3fe5e5c615c151baae53d7e3a05cad618d4e10e70377df": F_PREFIX}
# The kept addresses: noreply@anthropic.com, and a third party's public contact in round 4's ledger, by sha256,
# which ParcelRound's own gate keeps too. Reserved names are kept as a class (RFC 2606, RFC 6761).
KEPT_ADDRESSES = {"noreply@anthropic.com"}
KEPT_ADDRESS_HASHES = {"67fb808b9a8efff2590d0859b2c92f6864436515d8ca8bf421ad731cf7a45865"}
RESERVED = re.compile(r"(?i)(^|\.)(example\.(com|org|net)|example|invalid|test|localhost)$")

# ---- check 2: the repository the kit keeps you away from. Each form is one alternative, and each has a plant of its
# own. github.com's form takes any owner, so it holds Logan's pages, every fork's, git's scp-like remote
# (github.com:owner/repo) and codeload.github.com's form, which contains it. ----
_OWNER, _REPO = cat("loganw", "234"), cat("cft", "-fp256")
_ANY_OWNER = r"[A-Za-z0-9_.-]+"
CFT_FORMS = [
    ("github", r"github\.com[/:]" + _ANY_OWNER + "/" + _REPO),
    ("api", r"api\.github\.com/repos/" + _ANY_OWNER + "/" + _REPO),
    ("raw", r"raw\.githubusercontent\.com/" + _ANY_OWNER + "/" + _REPO),
    ("pages", r"[A-Za-z0-9-]+\.github\.io/" + _REPO),
]
CFT_URL = re.compile(r"(?i)(?:" + "|".join(p for _, p in CFT_FORMS) + r")(?![A-Za-z0-9_-])")


def url_spellings(text):
    """The text with its backslashes dropped (round 5's briefs/P1.md:74 held a regex-escaped URL), and then with its
    percent-encoding undone, up to three times, for a URL carried inside another."""
    out = [text.replace("\\", "")]
    for _ in range(3):
        nxt = urllib.parse.unquote(out[-1])
        if nxt == out[-1]:
            break
        out.append(nxt)
    return out


# ---- check 3: the arithmetic list. Word-bounded, case-insensitive. "escalation" is not on it: the methods use it
# for the urgent channel, and the record's other sense, a path to more digits, is caught by "precision". "round",
# "floor" and "ceil" are not on it either: the methods use each as a plain word ("round 6", "the floor"). ----
TERMS = [
    r"sticky", r"guard bits?", r"round bits?", r"subnormals?", r"denormals?", r"mantissas?", r"significands?",
    r"fma", r"fused multiply[- ]add", r"ulps?", r"tininess", r"underflow(?:s|ed)?", r"overflow(?:s|ed)?",
    r"softfloat", r"testfloat", r"rne", r"rtz", r"rmm", r"rdn", r"rup", r"rounding", r"rounded",
    r"round[- ]to(?:[- ](?:odd|nearest|even|zero))?", r"nans?", r"qnans?", r"snans?", r"infinit(?:y|ies)", r"inf",
    r"exponents?", r"normali[sz](?:e|ed|es|ation)", r"fp(?:16|32|64|128|256)", r"binary(?:16|32|64|128|256)",
    r"f(?:16|32|64)_\w*", r"(?:div|sqrt|rint|scaleb|cvt(?:to|from)?|conv|rem|nextup|nextdown|add|sub|mul|logb|class)"
    r"(?:16|32|64)\w*", r"conv(?:16|32|64)to(?:16|32|64)\w*", r"cvtto\w*", r"cvtfrom\w*", r"divsqrt\w*",
    r"divfull\w*", r"rsqrt\w*", r"scaleb", r"rint", r"nextup", r"nextdown", r"logb", r"divisions?",
    r"divid(?:e|es|ed|end|ends|ing)", r"divisors?", r"square[- ]roots?", r"reciprocals?", r"recip_\w*", r"newton",
    r"goldschmidt", r"binades?", r"2\^-?[0-9]+", r"encodings?", r"precision", r"enclosures?", r"cancellation",
    r"limbs?", r"mpfloat\w*", r"cft_mp_\w*", r"bound_(?:half|double)", r"inexact", r"invalid operation",
    r"signed zeros?", r"widening", r"narrowing", r"augmented", r"modular inverse", r"transcend\w*",
    r"exp2", r"expm1", r"log1p", r"log2", r"payne[- ]hanek", r"ln2", r"hard[- ]?cases?", r"exact[- ]quotients?",
    r"strip[- ]ties?", r"closest[- ]approach", r"clause[ -]?5\w*", r"cft_golden", r"golden", r"host/src", r"libcft",
    r"mpfr", r"mpmath", r"gmpy2", r"ucbtest", r"fpgen", r"core-math",
    r"(?:roundeven|nearbyint|l?lrint|l?lround|fmod|remquo|fmin|fmax|fdim|frexp|ldexp|copysign|signbit|fpclassify"
    r"|issignaling|issubnormal|totalorder|minnum|maxnum|minmag|maxmag|hypot|cbrt|ilogb|nextafter|nexttoward|fabs)"
    r"[fl]?", r"isnan", r"isinf", r"isfinite", r"trunc[fl]?", r"quantize",
]
TERM_RE = re.compile(r"(?i)(?<![A-Za-z0-9_])(?:" + "|".join(TERMS) + r")(?![A-Za-z0-9_])")
# The files the builder writes from that repository's record, or that quote it (KIT-0 section 3, item 1).
TERM_FILES = ["OWNER.md", "GLOSSARY.md", "METRICS.md", "AGENTS.md"]
TERM_DIRS = ["examples/cases"]


REPO_NAME = re.compile(r"(?i)(?<![A-Za-z0-9_])cft-fp256(?![A-Za-z0-9_])")


def term_hit(line):
    """The first listed term on the line, or None. The repository's own name is not a term, though it ends in one."""
    m = TERM_RE.search(REPO_NAME.sub("", line))
    return m.group(0) if m else None


# ---- check 4: shapes after QRO-Crate's tools/check_privacy.py, ALTERNATIVES ----
_NAME = r"[^\W_][\w.-]*"
_KEY = r"""\s{0,16}["']?\s{0,16}[=:]\s{0,16}["']?(?:Bearer\s{1,16}|apikey\s{1,16})?[A-Za-z0-9._~+/-]{24,}"""
PRIVACY = [
    ("path", "windows-home", r"(?i)(?<![A-Za-z0-9])[a-z]:[\\/]+(users|documents and settings)[\\/]+" + _NAME),
    ("path", "driveless-home", r"(?i)(?<![A-Za-z0-9.:\\])\\users\\" + _NAME),
    ("path", "git-bash-home", r"(?i)(?<![A-Za-z0-9.])/[a-z]/users/" + _NAME),
    ("path", "wsl-mount-home", r"(?i)(?<![A-Za-z0-9.])/mnt/[a-z]/users/" + _NAME),
    ("path", "cygwin-home", r"(?i)(?<![A-Za-z0-9.])/cygdrive/[a-z]/users/" + _NAME),
    ("path", "docker-host-home", r"(?i)(?<![A-Za-z0-9.])(/host_mnt|/run/desktop/mnt/host)/[a-z]/users/" + _NAME),
    ("path", "posix-home", r"(?i)(?<![A-Za-z0-9.])/(users|home)/" + _NAME),
    ("path", "backslash-home", r"(?i)(?<![A-Za-z0-9.:\\])\\home\\" + _NAME),
    ("path", "wsl-unc", r"(?i)\\\\wsl(\$|\.localhost)\\"),
    ("path", "url-quoted-home", r"(?i)%2F(users|home)%2F|[a-z]%3A(%5C|%2F)users(%5C|%2F)"),
    ("path", "file-url-home", r"(?i)(?<![A-Za-z0-9])[a-z]%3a/+(users|documents%20and%20settings)/+" + _NAME),
    ("path", "var-home", r"(?i)(?<![A-Za-z0-9.])/var/home/" + _NAME),
    ("path", "unc-home", r"(?i)\\\\[^\\\s]+\\(home|users)\\" + _NAME),
    ("path", "remote-uri-home", r"(?i)\b(vscode-remote|ssh|sftp|scp|smb|nfs|rsync|ftps?|file)://[^/\s]*/(home|users)/"
     + _NAME),
    ("key", "crn", r"(?i)crn(:|%3a|\\u003a)v1(:|%3a|\\u003a)[A-Za-z0-9:%._/\\-]*"),
    ("key", "named:QISKIT_IBM_TOKEN", r"(?i)QISKIT_IBM_TOKEN" + _KEY),
    ("key", "named:IBM_QUANTUM_TOKEN", r"(?i)IBM_QUANTUM_TOKEN" + _KEY),
    ("key", "named:IBMQ_TOKEN", r"(?i)IBMQ_TOKEN" + _KEY),
    ("key", "named:QF_IBM_KEY", r"(?i)QF_IBM_KEY" + _KEY),
    ("key", "named:api-key", r"(?i)api[_-]?key" + _KEY),
    ("key", "named:token", r"(?i)(?<![A-Za-z0-9])token" + _KEY),
    ("key", "named:camelToken", r"(?<=[a-z0-9])Token(?i:" + _KEY + ")"),
    # QRO-Crate's "named:x-api-key" is left out: named:api-key above matches inside every x-api-key, so a control
    # for it is caught by api-key and tests nothing of its own (ParcelRound METHOD.md section 5).
    ("key", "named:authorization", r"(?i)authorization" + _KEY),
    ("key", "bearer", r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{24,}"),
    ("key", "jwt", r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ("key", "ibm-id", r"\bIBMid-[A-Za-z0-9]{6,}"),
    ("key", "ibm-service-id", r"(?i)\biam-ServiceId-[0-9a-f-]{20,}"),
    ("key", "ibm-account", r"(?i)account_?id[\"':=\s]{1,6}[0-9a-f]{32}\b|\ba/[0-9a-f]{32}\b"),
    ("key", "moth-key", r"\bmoth_(?=[A-Za-z0-9]*[0-9])[A-Za-z0-9]{20,}\b"),
    ("key", "presigned-url", r"(?i)(X-Amz-Signature|X-Amz-Credential|X-Goog-Signature|X-Goog-Credential)="
                             r"[A-Za-z0-9%/._-]{16,}"),
    ("key", "aws-key-id", r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("ip", "private-ipv4", r"(?<![\d.])(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}(?![\d.])"),
]
PRIVACY_RE = [(k, n, re.compile(p)) for k, n, p in PRIVACY]
# A literal, lower-cased, that each shape cannot match without: the pattern runs only on a text holding one of its
# needles, which saves scanning 14 MB once a shape. A shape with no entry here always runs. --control holds this
# table: every plant is found through it, and so is every spelling of every plant with a letter re folds.
NEEDLES = {
    "windows-home": ("users", "documents and settings"), "driveless-home": ("\\users\\",),
    "git-bash-home": ("/users/",), "wsl-mount-home": ("/mnt/",), "cygwin-home": ("/cygdrive/",),
    "docker-host-home": ("/host_mnt", "/run/desktop/mnt/host"), "posix-home": ("/users/", "/home/"),
    "backslash-home": ("\\home\\",), "wsl-unc": ("\\\\wsl",), "url-quoted-home": ("%2f", "%3a"),
    "file-url-home": ("%3a",), "var-home": ("/var/home/",), "unc-home": ("\\\\",), "remote-uri-home": ("://",),
    "crn": ("crn",), "named:QISKIT_IBM_TOKEN": ("qiskit_ibm_token",), "named:IBM_QUANTUM_TOKEN": ("ibm_quantum_token",),
    "named:IBMQ_TOKEN": ("ibmq_token",), "named:QF_IBM_KEY": ("qf_ibm_key",), "named:api-key": ("api",),
    "named:token": ("token",), "named:camelToken": ("token",), "named:authorization": ("authorization",),
    "bearer": ("bearer",), "jwt": ("eyj",), "ibm-id": ("ibmid-",), "ibm-service-id": ("iam-serviceid-",),
    "ibm-account": ("account", "a/"), "moth-key": ("moth_",), "presigned-url": ("x-amz-", "x-goog-"),
    "aws-key-id": ("akia", "asia"), "private-ipv4": ("10.", "172.", "192.168"),
}
# re's case-insensitive matching takes four letters beyond ASCII for ASCII ones (its documentation names them: a
# dotted capital I and a dotless i for i, a long s for s, and the Kelvin sign for k). str.lower() writes the dotted I
# as an i and a combining dot, and keeps the dotless i and the long s. So the text is folded as re folds it, and only
# then lowered, before the needles are sought.
FOLD = str.maketrans({"\u0130": "i", "\u0131": "i", "\u017f": "s", "\u212a": "k"})
ADDRESS = re.compile(r"(?<![A-Za-z0-9._%+-])([A-Za-z0-9._%+-]+)@((?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,})")
ESCAPED_ADDRESS = re.compile(r"(?i)(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+(\\u0040|\[at\]|\(at\))"
                             r"((?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,})")
USER_AT_HOST = re.compile(r"(?<![A-Za-z0-9._%+-])([A-Za-z0-9._-]+)@([A-Za-z0-9][A-Za-z0-9.-]*)")
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{3,40}")
ALNUM = re.compile(r"[A-Za-z0-9]+")

# The findings check 4 gives besides its shapes. --control plants each one, by this name.
F_PERSONAL = "an address at a personal domain"
F_UNKEPT = "an address that is not one of the kept ones"
F_ESCAPED = "an escaped address"
F_USER_AT_HOST = "a user@host that names Logan's user name or his desktop's name"
F_MACHINE = "the name of Logan's desktop"
F_IDENTITY = "a commit identity holds an address that is neither kept nor Logan's"
F_UNREADABLE = "git cannot read this bundle, so nothing inside it is checked"


def address_kept(local, domain):
    a = f"{local}@{domain}".lower()
    return a in KEPT_ADDRESSES or sha(a) in KEPT_ADDRESS_HASHES or bool(RESERVED.search(domain.lower()))


def privacy_findings(text, users, machines, domains, fragments=FRAGMENTS):
    out = []
    low = text.translate(FOLD).lower()
    for kind, name, rx in PRIVACY_RE:
        needles = NEEDLES.get(name)
        if needles is not None and not any(n in low for n in needles):
            continue
        if rx.search(text):
            out.append(f"{kind} shape {name}")
    if "@" in text:
        for m in ADDRESS.finditer(text):
            if not address_kept(m.group(1), m.group(2)):
                out.append(F_PERSONAL if sha(m.group(2).lower()) in domains else F_UNKEPT)
        for m in USER_AT_HOST.finditer(text):
            u, h = m.group(1), m.group(2).rstrip(".")
            if sha(u) in users or sha(u.lower()) in users or sha(h) in machines or sha(h.lower()) in machines:
                out.append(F_USER_AT_HOST)
    if any(n in low for n in ("\\u0040", "[at]", "(at)")):
        for m in ESCAPED_ADDRESS.finditer(text):
            if not RESERVED.search(m.group(2).lower()):
                out.append(F_ESCAPED)
                break
    for t in set(TOKEN.findall(text)):
        if sha(t) in machines or sha(t.lower()) in machines:
            out.append(F_MACHINE)
            break
    for t in set(ALNUM.findall(text)):
        name = fragments.get(sha(t.lower()))
        if name:
            out.append(name)
    return sorted(set(out))


# ---- reading what the kit holds: files, archive members, and the bundle's blobs, messages and identities ----
BOMS = ((b"\x00\x00\xfe\xff", "utf-32-be"), (b"\xff\xfe\x00\x00", "utf-32-le"), (b"\xef\xbb\xbf", "utf-8-sig"),
        (b"\xfe\xff", "utf-16-be"), (b"\xff\xfe", "utf-16-le"))


def decode(data):
    for bom, enc in BOMS:
        if data.startswith(bom):
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                break
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")          # read every byte: a binary file is searched as well


def need_git():
    if shutil.which("git") is None:
        print("check_kit: git is not on PATH, and the QRO-Crate bundle cannot be read without it; nothing passes")
        sys.exit(2)


_BUNDLES = {}


def bundle_texts(bundle):
    """(where, text) for every blob of every commit of the bundle, every commit message, and (identity, email) for
    every commit's author and committer, read through a temporary clone. Read once per process for each content of
    a bundle (the checks share it), and every blob in one `git cat-file --batch`. A bundle git cannot clone gives
    (None, None, git's message)."""
    need_git()
    digest = hashlib.sha256(Path(bundle).read_bytes()).hexdigest()
    if digest in _BUNDLES:
        return _BUNDLES[digest]
    texts, identities = [], []
    with tempfile.TemporaryDirectory() as t:
        r = subprocess.run(["git", "clone", "-q", "--bare", str(bundle), t + "/b.git"], capture_output=True, text=True)
        if r.returncode != 0:
            _BUNDLES[digest] = (None, None, r.stderr.strip() or "git clone exit %d" % r.returncode)
            return _BUNDLES[digest]
        g = ["git", "--git-dir", t + "/b.git"]
        commits = subprocess.run(g + ["rev-list", "--all"], capture_output=True, text=True, check=True).stdout.split()
        if not commits:
            _BUNDLES[digest] = (None, None, "the bundle holds no commit")
            return _BUNDLES[digest]
        seen, wanted = set(), []
        for c in commits:
            msg = subprocess.run(g + ["log", "-1", "--format=%B", c], capture_output=True, text=True,
                                 check=True).stdout
            texts.append((f"commit {c[:12]} message", msg))
            who = subprocess.run(g + ["log", "-1", "--format=%ae%n%ce", c], capture_output=True, text=True,
                                 check=True).stdout.split()
            identities.extend((c, e) for e in who)
            tree = subprocess.run(g + ["ls-tree", "-r", c], capture_output=True, text=True, check=True).stdout
            for line in tree.splitlines():
                meta, path = line.split("\t", 1)
                mode, typ, oid = meta.split()
                if typ != "blob" or oid in seen:
                    continue
                seen.add(oid)
                wanted.append(len(texts))
                texts.append((f"commit {c[:12]} {path}", oid))
        out = subprocess.run(g + ["cat-file", "--batch"], input="".join(texts[i][1] + "\n" for i in wanted).encode(),
                             capture_output=True, check=True).stdout
        pos = 0
        for i in wanted:
            nl = out.index(b"\n", pos)
            oid, typ, size = out[pos:nl].decode().split()
            if oid != texts[i][1] or typ != "blob":
                raise RuntimeError(f"git cat-file --batch answered {oid} {typ} for {texts[i][1]}")
            texts[i] = (texts[i][0], out[nl + 1:nl + 1 + int(size)])
            pos = nl + 1 + int(size) + 1
    _BUNDLES[digest] = (texts, identities, None)
    return _BUNDLES[digest]


def kit_files(kit):
    return sorted(p for p in kit.rglob("*") if p.is_file())


def every_text(kit, only=None):
    """(where, bytes) for every file, every archive member, and every bundle blob and message. A bundle git cannot
    read contributes its raw bytes; unreadable_bundles() names it, and checks 2 and 4 refuse it."""
    out = []
    for p in kit_files(kit):
        rel = p.relative_to(kit).as_posix()
        if only is not None and rel not in only:
            continue
        data = p.read_bytes()
        if p.suffix == ".zip":
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    for i in z.infolist():
                        if not i.is_dir():
                            out.append((f"{rel}:{i.filename}", z.read(i)))
            except zipfile.BadZipFile:
                out.append((rel, data))
        elif p.suffix == ".bundle":
            texts, _, err = bundle_texts(p)
            if texts is None:
                out.append((rel, data))
            else:
                out.extend((f"{rel}: {w}", d if isinstance(d, bytes) else d.encode("utf-8")) for w, d in texts)
        else:
            out.append((rel, data))
    return out


def unreadable_bundles(kit, only=None):
    """(path, git's message) for each bundle in the kit that git cannot read."""
    found = []
    for p in kit_files(kit):
        rel = p.relative_to(kit).as_posix()
        if p.suffix == ".bundle" and (only is None or rel in only):
            texts, _, err = bundle_texts(p)
            if texts is None:
                found.append((rel, err))
    return found


# ---- the checks; each returns a list of findings ----
def check_manifest(kit, only=None):
    f = []
    man = kit / "MANIFEST.txt"
    if not man.is_file():
        return ["MANIFEST.txt is missing"]
    listed = {}
    for line in man.read_text(encoding="utf-8").splitlines():
        m = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if m:
            listed[m.group(2)] = m.group(1)
    if not any(l.startswith("source ") for l in man.read_text(encoding="utf-8").splitlines()):
        f.append("MANIFEST.txt names no source commit")
    present = {p.relative_to(kit).as_posix() for p in kit_files(kit) if p.name != "MANIFEST.txt"}
    for rel in sorted(present - set(listed)):
        f.append(f"{rel}: in the kit but not in MANIFEST.txt")
    for rel in sorted(set(listed) - present):
        f.append(f"{rel}: in MANIFEST.txt but missing from the kit")
    for rel in sorted(set(listed) & present):
        if hashlib.sha256((kit / rel).read_bytes()).hexdigest() != listed[rel]:
            f.append(f"{rel}: its sha256 does not match MANIFEST.txt")
    for where, data in every_text(kit, only):
        if where.lower().endswith(".pdf") or data[:5] == b"%PDF-":
            f.append(f"{where}: a PDF (the kit holds none)")
    return f


LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REFDEF = re.compile(r"(?m)^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s|$)")


def check_links(kit, only=None):
    f = []
    for p in kit_files(kit):
        rel = p.relative_to(kit).as_posix()
        if p.suffix != ".md" or (only is not None and rel not in only):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        text_nocode = re.sub(r"(?s)```.*?```", "", text)
        for m in list(LINK.finditer(text_nocode)) + list(REFDEF.finditer(text_nocode)):
            target = m.group(1)
            if re.match(r"(?i)[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            path = target.split("#", 1)[0].split("?", 1)[0]
            path = re.sub(r"%20", " ", path)
            if not path:
                continue
            dest = (p.parent / path).resolve()
            try:
                dest.relative_to(kit.resolve())
            except ValueError:
                f.append(f"{rel}: link '{target}' leaves the kit")
                continue
            if not dest.exists():
                f.append(f"{rel}: link '{target}' does not resolve")
    for where, data in every_text(kit, only):
        for text in url_spellings(decode(data)):
            m = CFT_URL.search(text)
            if m:
                f.append(f"{where}: a URL into the repository the kit keeps you away from ({m.group(0)[:22]}...)")
                break
    for rel, err in unreadable_bundles(kit, only):
        f.append(f"{rel}: {F_UNREADABLE} ({err[:80]})")
    return f


def check_terms(kit, only=None):
    f = []
    files = [kit / n for n in TERM_FILES] + [p for d in TERM_DIRS for p in sorted((kit / d).glob("*.md"))]
    for p in files:
        rel = p.relative_to(kit).as_posix()
        if only is not None and rel not in only:
            continue
        if not p.is_file():
            f.append(f"{rel}: missing (check 3 reads it)")
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            t = term_hit(line)
            if t:
                f.append(f"{rel}:{n}: holds '{t}', a term of the arithmetic list")
    return f


def check_privacy(kit, only=None, users=USER_NAMES, machines=MACHINE_NAMES, domains=PERSONAL_DOMAINS,
                  fragments=FRAGMENTS):
    f = []
    for where, data in every_text(kit, only):
        for finding in privacy_findings(decode(data), users, machines, domains, fragments):
            f.append(f"{where}: {finding}")
    for p in kit_files(kit):
        rel = p.relative_to(kit).as_posix()
        if p.suffix == ".bundle" and (only is None or rel in only):
            _, identities, err = bundle_texts(p)
            for c, email in identities or []:
                local, _, domain = email.partition("@")
                if not (address_kept(local, domain) or sha(domain.lower()) in domains):
                    f.append(f"{rel}: commit {c[:12]}: {F_IDENTITY}")
    for rel, err in unreadable_bundles(kit, only):
        f.append(f"{rel}: {F_UNREADABLE} ({err[:80]})")
    return f


TABLE_ROW = re.compile(r"^\|[^|]*\|\s*\d+\s*\|\s*\[([^\]]+)\]\([^)]+\)\s*\|\s*([\d,]+)\s*\|$")
CASES_ROW = re.compile(r"^\|\s*\[cases/([^\]]+)\]\([^)]+\)\s*\|[^|]*\|\s*([^|]+?)\s*\|$")


def block(text, name):
    a, b = f"<!-- {name}:begin -->", f"<!-- {name}:end -->"
    if text.count(a) != 1 or text.count(b) != 1:
        return None
    return text[text.index(a) + len(a):text.index(b)]


def check_generated(kit, only=None):
    f = []
    sh = kit / "START-HERE.md"
    blk = block(sh.read_text(encoding="utf-8"), "reading") if sh.is_file() else None
    if blk is None:
        f.append("START-HERE.md: no reading table between its markers")
    else:
        rows = [TABLE_ROW.match(l) for l in blk.splitlines() if l.startswith("|") and "---" not in l]
        rows = [r for r in rows if r]
        if not rows:
            f.append("START-HERE.md: the reading table has no rows")
        for r in rows:
            p = kit / r.group(1)
            if not p.is_file():
                f.append(f"START-HERE.md: the reading table names {r.group(1)}, which is not in the kit")
            elif p.stat().st_size != int(r.group(2).replace(",", "")):
                f.append(f"START-HERE.md: the reading table says {r.group(1)} is {r.group(2)} bytes; it is "
                         f"{p.stat().st_size:,}")
    ex = kit / "examples" / "README.md"
    blk = block(ex.read_text(encoding="utf-8"), "cases") if ex.is_file() else None
    if blk is None:
        f.append("examples/README.md: no sample table between its markers")
    else:
        listed = set()
        for l in blk.splitlines():
            r = CASES_ROW.match(l)
            if not r:
                continue
            listed.add(r.group(1))
            p = kit / "examples" / "cases" / r.group(1)
            if not p.is_file():
                f.append(f"examples/README.md: the table names cases/{r.group(1)}, which is not in the kit")
                continue
            ids = [x.strip() for x in r.group(2).split(",")]
            held = re.findall(r"(?m)^## ([0-9]+[a-z]?)\. ", p.read_text(encoding="utf-8"))
            if ids != held:
                f.append(f"examples/README.md: cases/{r.group(1)} is listed with {ids}; it holds {held}")
        for p in sorted((kit / "examples" / "cases").glob("*.md")):
            if p.name not in listed:
                f.append(f"examples/cases/{p.name}: not in examples/README.md's table")
    return f


CHECKS = [("manifest", check_manifest), ("links", check_links), ("terms", check_terms),
          ("privacy", check_privacy), ("generated", check_generated)]


def run(kit):
    total = 0
    for name, fn in CHECKS:
        found = fn(kit)
        total += len(found)
        print(f"{name:10} {'ok' if not found else 'REFUSED'}" + ("" if not found else f"  {len(found)} finding(s)"))
        for x in found:
            print(f"           {x}")
    print("VERDICT: " + ("PASS, all five checks hold" if total == 0 else f"REFUSED, {total} finding(s)"))
    return 0 if total == 0 else 1


# ---- --control: one plant for each finding; each in a fresh copy; restored by discarding the copy ----
def refresh_manifest(kit):
    man = kit / "MANIFEST.txt"
    head = [l for l in man.read_text(encoding="utf-8").splitlines() if not re.fullmatch(r"[0-9a-f]{64}  .+", l)]
    lines = head[:]
    for p in kit_files(kit):
        if p.name != "MANIFEST.txt":
            lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(kit).as_posix()}")
    man.write_text("\n".join(lines) + "\n", encoding="utf-8")


CONTROL_USER = cat("ctrl", "owner")
CONTROL_MACHINE = cat("CTRL-", "BENCH7")
CONTROL_DOMAIN = cat("owner-", "control.net")
CONTROL_LABEL = cat("ctrl", "mailhouse")
CONTROL_PREFIX = cat("c0ffee", "42")


def privacy_samples():
    """One sample of each path and key shape, built at run time."""
    return {
        "windows-home": cat("C:", "\\Users\\", "someone"), "driveless-home": cat("\\", "users\\", "someone"),
        "git-bash-home": cat("/c/", "users/", "someone"), "wsl-mount-home": cat("/mnt/c/", "users/", "someone"),
        "cygwin-home": cat("/cygdrive/c/", "users/", "someone"),
        "docker-host-home": cat("/host_mnt/c/", "users/", "someone"),
        "posix-home": cat("/ho", "me/", "someone"), "backslash-home": cat("\\", "home\\", "someone"),
        "wsl-unc": cat("\\\\", "wsl$\\", "x"), "url-quoted-home": cat("%2F", "home%2F", "x"),
        "file-url-home": cat("c%3a/", "users/", "someone"), "var-home": cat("/var/", "home/", "someone"),
        "unc-home": cat("\\\\server\\", "home\\", "someone"), "remote-uri-home": cat("ssh", "://host/", "home/someone"),
        "crn": cat("crn", ":v1:", "bluemix:public:x"),
        "named:QISKIT_IBM_TOKEN": cat("QISKIT_IBM_", "TOKEN=", "A" * 30),
        "named:IBM_QUANTUM_TOKEN": cat("IBM_QUANTUM_", "TOKEN=", "A" * 30),
        "named:IBMQ_TOKEN": cat("IBMQ_", "TOKEN=", "A" * 30), "named:QF_IBM_KEY": cat("QF_IBM_", "KEY=", "A" * 30),
        "named:api-key": cat("api_", "key=", "A" * 30), "named:token": cat("to", "ken=", "A" * 30),
        "named:camelToken": cat("access", "Token=", "A" * 30),
        "named:authorization": cat("Authori", "zation: ", "A" * 30),
        "bearer": cat("Bea", "rer ", "A" * 30), "jwt": cat("ey", "J", "a" * 12, ".", "b" * 12, ".", "c" * 12),
        "ibm-id": cat("IBM", "id-", "ABC123"), "ibm-service-id": cat("iam-", "ServiceId-", "0123456789abcdef0123"),
        "ibm-account": cat("account_", "id: ", "0" * 32), "moth-key": cat("mo", "th_", "abc1234567890defghij"),
        "presigned-url": cat("X-Amz-", "Signature=", "a" * 20), "aws-key-id": cat("AK", "IA", "ABCDEFGHIJKLMNOP"),
        "private-ipv4": cat("host 10.", "1.2.3"),
    }


def plants():
    """(name, check, how, refresh, want) for each finding. `how` changes a copy and returns the set of files to read,
    or None for all; `want` is the text the finding must hold. Every planted string is built at run time (cat)."""
    P = []

    def append_to(rel, s):
        def how(k):
            p = k / rel
            p.write_bytes(p.read_bytes() + b"\n" + s.encode("utf-8") + b"\n")
            return {rel}
        return how

    def edit(rel, old, new):
        def how(k):
            p = k / rel
            t = p.read_text(encoding="utf-8")
            if t.count(old) < 1:
                raise RuntimeError(f"the control's text is not in {rel}: {old[:40]!r}")
            p.write_text(t.replace(old, new, 1), encoding="utf-8")
            return None
        return how

    def zip_member(name, body):
        def how(k):
            rel = "method/parcelround/archive/round6-ledger.zip"
            buf = io.BytesIO()
            with zipfile.ZipFile(k / rel) as src, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as dst:
                for i in src.infolist():
                    dst.writestr(i, src.read(i))
                dst.writestr("parcelround-r6-ledger/" + name, body)
            (k / rel).write_bytes(buf.getvalue())
            return {rel}
        return how

    def bundle_plant(where, body=None, email=cat("control", "@example.com")):
        def how(k):
            need_git()
            rel = "reference/QRO-Crate.bundle"
            with tempfile.TemporaryDirectory() as t:
                g = lambda *a: subprocess.run(["git", "-C", t + "/w"] + list(a), capture_output=True, check=True)
                subprocess.run(["git", "clone", "-q", "-b", "main", str(k / rel), t + "/w"], capture_output=True,
                               check=True)
                msg = cat("planted ", body) if where == "message" else "planted"
                if where == "blob":
                    Path(t + "/w/planted.md").write_bytes(body if isinstance(body, bytes) else body.encode("utf-8"))
                    g("add", "planted.md")
                g("-c", "user.name=control", "-c", "user.email=" + email, "-c", "commit.gpgsign=false", "commit", "-q",
                  "--allow-empty", "-m", msg)
                g("bundle", "create", "-q", t + "/new.bundle", "refs/heads/main")
                shutil.copy(t + "/new.bundle", k / rel)
            return {rel}
        return how

    def cut_bundle(k):
        rel = "reference/QRO-Crate.bundle"
        data = (k / rel).read_bytes()
        (k / rel).write_bytes(data[:data.index(b"\n\n") + 2])
        return {rel}

    pdf = cat("%PD", "F-1.7\n")
    # check 1
    P.append(("a changed byte", "manifest", append_to("ROLES.md", " "), False, "does not match MANIFEST.txt"))
    P.append(("an extra file", "manifest", lambda k: ((k / "extra.txt").write_text("x"), None)[1], False,
              "in the kit but not in MANIFEST.txt"))
    P.append(("a missing file", "manifest", lambda k: ((k / "GLOSSARY.md").unlink(), None)[1], False,
              "missing from the kit"))
    P.append(("no MANIFEST.txt", "manifest", lambda k: ((k / "MANIFEST.txt").unlink(), None)[1], False,
              "MANIFEST.txt is missing"))
    P.append(("a manifest that names no source", "manifest",
              lambda k: ((k / "MANIFEST.txt").write_text("".join(
                  l + "\n" for l in (k / "MANIFEST.txt").read_text(encoding="utf-8").splitlines()
                  if not l.startswith("source ")), encoding="utf-8"), None)[1], False,
              "names no source commit"))
    P.append(("a PDF", "manifest", lambda k: ((k / "standard.pdf").write_bytes(pdf.encode()), None)[1], True,
              "a PDF"))
    P.append(("a PDF inside an archive member", "manifest", zip_member("standard.bin", pdf), True, "a PDF"))
    P.append(("a PDF in a bundle blob", "manifest", bundle_plant("blob", pdf.encode()), True, "a PDF"))
    # check 2
    P.append(("a broken relative link", "links", append_to("ROLES.md", "[gone](no-such-file.md)"), True,
              "does not resolve"))
    P.append(("a relative link out of the kit", "links", append_to("ROLES.md", "[out](../../outside.md)"), True,
              "leaves the kit"))
    url = cat("https", "://", "github", ".com/", _OWNER, "/", _REPO)
    forms = {"github": url, "github, a fork": cat("https", "://", "github", ".com/", "someone/", _REPO),
             "github, git's scp-like remote": cat("git", "@", "github", ".com:", _OWNER, "/", _REPO, ".git"),
             "api": cat("https", "://", "api.github", ".com/repos/", _OWNER, "/", _REPO),
             "raw": cat("https", "://", "raw.githubuser", "content.com/", _OWNER, "/", _REPO, "/main/x"),
             "pages": cat("https", "://", _OWNER, ".github", ".io/", _REPO),
             "pages, its dots escaped": cat(_OWNER, "\\", ".github\\", ".io/", _REPO),
             "github, percent-encoded inside a redirect": cat("https", "://example.invalid/r?to=https%3A%2F%2F",
                                                              "github", ".com%2F", _OWNER, "%2F", _REPO)}
    for name, u in forms.items():
        P.append((f"a URL, {name}", "links", append_to("ROLES.md", cat("see ", u, " here")), True,
                  "a URL into the repository"))
    for name in ("github", "api", "raw", "pages"):
        P.append((f"a URL, {name}, inside an archive member", "links", zip_member("planted.md", forms[name] + "\n"),
                  True, "a URL into the repository"))
    P.append(("a URL in a bundle blob", "links", bundle_plant("blob", url + "\n"), True, "a URL into the repository"))
    P.append(("a URL in a bundle commit message", "links", bundle_plant("message", url), True,
              "a URL into the repository"))
    P.append(("a bundle git cannot read, for check 2", "links", cut_bundle, True, F_UNREADABLE))
    # check 3
    first_case = lambda k: sorted((k / "examples/cases").glob("*.md"))[0].relative_to(k).as_posix()
    P.append(("an arithmetic term in a sample", "terms",
              lambda k: append_to(first_case(k), cat("the ", "sti", "cky bit"))(k), True, "a term of the arithmetic"))
    P.append(("a file check 3 reads, missing", "terms", lambda k: ((k / "METRICS.md").unlink(), None)[1], True,
              "missing (check 3 reads it)"))
    # check 4: each path, key and address shape, each private range, the names (control names)
    for name, s in privacy_samples().items():
        if name != "private-ipv4":
            P.append((f"a {name} shape", "privacy", append_to("ROLES.md", s), True, f"shape {name}"))
    for rng, ip in (("10/8", cat("10.", "1.2.3")), ("172.16/12", cat("172.", "20.1.1")),
                    ("192.168/16", cat("192.", "168.0.7"))):
        P.append((f"a private address in {rng}", "privacy", append_to("ROLES.md", cat("host ", ip)), True,
                  "shape private-ipv4"))
    P.append(("an address that is not a kept one", "privacy", append_to("ROLES.md", cat("someone", "@", "unkept.net")),
              True, F_UNKEPT))
    P.append(("an escaped address", "privacy", append_to("ROLES.md", cat("someone", "[at]", "unkept.net")), True,
              F_ESCAPED))
    P.append(("an address escaped as \\u0040", "privacy",
              append_to("ROLES.md", cat("someone", "\\u00", "40unkept.net")), True, F_ESCAPED))
    P.append(("an address at a personal domain (control)", "privacy",
              append_to("ROLES.md", cat("x", "@", CONTROL_DOMAIN)), True, F_PERSONAL))
    P.append(("a user@host naming Logan's user name (control)", "privacy",
              append_to("ROLES.md", cat(CONTROL_USER, "@", "somehost")), True, F_USER_AT_HOST))
    P.append(("a user@host naming his desktop (control)", "privacy",
              append_to("ROLES.md", cat("someone", "@", CONTROL_MACHINE)), True, F_USER_AT_HOST))
    P.append(("his desktop's name (control)", "privacy", append_to("ROLES.md", cat("on ", CONTROL_MACHINE)), True,
              F_MACHINE))
    P.append(("his email domain's name, alone (control)", "privacy",
              append_to("ROLES.md", cat("the ", CONTROL_LABEL, " account")), True, F_LABEL))
    P.append(("his account id's prefix (control)", "privacy",
              append_to("ROLES.md", cat("ids starting ", CONTROL_PREFIX, "-1234")), True, F_PREFIX))
    P.append(("a bundle commit whose identity is neither kept nor his", "privacy",
              bundle_plant("message", "x", email=cat("someone", "@", "unkept.net")), True, F_IDENTITY))
    P.append(("a bundle git cannot read, for check 4", "privacy", cut_bundle, True, F_UNREADABLE))
    # check 5
    def stale_table(k):
        p = k / "START-HERE.md"
        t = p.read_text(encoding="utf-8")
        i = t.index("<!-- reading:begin -->")
        m = re.compile(r"\| ([\d,]+) \|\n").search(t, i)
        p.write_text(t[:m.start(1)] + m.group(1) + "1" + t[m.end(1):], encoding="utf-8")
        return None
    P.append(("a stale reading table", "generated", stale_table, True, "bytes; it is"))
    def missing_row(k):
        p = k / "START-HERE.md"
        t = p.read_text(encoding="utf-8")
        i = t.index("<!-- reading:begin -->")
        m = re.compile(r"\| \[([^\]]+)\]\(([^)]+)\) \|").search(t, i)
        p.write_text(t[:m.start()] + "| [NO-SUCH.md](NO-SUCH.md) |" + t[m.end():], encoding="utf-8")
        return None
    P.append(("a reading table that names a file the kit lacks", "generated", missing_row, True,
              "which is not in the kit"))
    P.append(("a reading table with no rows", "generated",
              lambda k: (k / "START-HERE.md").write_text(re.sub(
                  r"(?s)<!-- reading:begin -->.*<!-- reading:end -->", "<!-- reading:begin -->\n<!-- reading:end -->",
                  (k / "START-HERE.md").read_text(encoding="utf-8")), encoding="utf-8"), True, "has no rows"))
    P.append(("a reading table without its markers", "generated", edit("START-HERE.md", "<!-- reading:begin -->", ""),
              True, "no reading table between its markers"))
    def stale_cases(k):
        p = sorted((k / "examples/cases").glob("*.md"))[0]
        p.write_text(p.read_text(encoding="utf-8").replace("\n## ", "\n## 99z. planted\n\n## ", 1), encoding="utf-8")
        return None
    P.append(("a stale sample table", "generated", stale_cases, True, "is listed with"))
    P.append(("a sample table that names a file the kit lacks", "generated",
              lambda k: edit("examples/README.md", "[cases/", "[cases/x")(k), True, "which is not in the kit"))
    P.append(("a sample file the table leaves out", "generated",
              lambda k: ((k / "examples/cases/99-planted.md").write_text("## 99a. planted\n"), None)[1], True,
              "not in examples/README.md's table"))
    P.append(("a sample table without its markers", "generated", edit("examples/README.md", "<!-- cases:begin -->", ""),
              True, "no sample table between its markers"))
    return P


def fold_spellings(s):
    """Each spelling of s with one of its letters, or all of them, written as a letter re folds to it."""
    folds = {"i": ("\u0130", "\u0131"), "s": ("\u017f",), "k": ("\u212a",)}
    out = set()
    for letter, others in folds.items():
        at = [i for i, ch in enumerate(s) if ch.lower() == letter]
        for o in others:
            for i in at:
                out.add(s[:i] + o + s[i + 1:])
            if at:
                out.add("".join(o if ch.lower() == letter else ch for ch in s))
    return sorted(out)


def control(kit):
    need_git()
    users = USER_NAMES | {sha(CONTROL_USER)}
    machines = MACHINE_NAMES | {sha(CONTROL_MACHINE)}
    domains = PERSONAL_DOMAINS | {sha(CONTROL_DOMAIN)}
    fragments = dict(FRAGMENTS, **{sha(CONTROL_LABEL): F_LABEL, sha(CONTROL_PREFIX): F_PREFIX})
    fns = dict(CHECKS)
    missed = 0
    ps = plants()
    with tempfile.TemporaryDirectory() as t:
        pristine = Path(t) / "pristine"
        shutil.copytree(kit, pristine)
        for i, (name, check, how, refresh, want) in enumerate(ps, 1):
            copy = Path(t) / f"c{i}"
            shutil.copytree(pristine, copy)
            only = how(copy)
            if refresh and (copy / "MANIFEST.txt").is_file():
                refresh_manifest(copy)
            if check == "privacy":
                found = check_privacy(copy, only, users, machines, domains, fragments)
            else:
                found = fns[check](copy, only)
            hits = [x for x in found if want in x]
            missed += not hits
            print(f"{'caught' if hits else 'MISSED':7} {check:10} {name}" + (f"  ({hits[0][:90]})" if hits else ""))
            shutil.rmtree(copy)
        # the pristine copy must still pass every check it was planted against
        clean = sum(len(fn(pristine)) for _, fn in CHECKS)
    # every spelling of every path and key sample with a letter re folds must be found through the prefilter
    spellings = spelled_missed = 0
    by_name = {n: rx for _, n, rx in PRIVACY_RE}
    for name, s in privacy_samples().items():
        for v in fold_spellings(s):
            if not by_name[name].search(v):
                continue
            spellings += 1
            if not any(x.endswith(f"shape {name}") for x in privacy_findings(v, set(), set(), set(), {})):
                spelled_missed += 1
                print(f"MISSED  privacy    the {name} shape spelled {v!r}, which its pattern matches")
    print(f"prefilter: {spellings - spelled_missed} of {spellings} spellings found: each privacy sample written with "
          f"a letter re folds, where its pattern still matches")
    print(f"CONTROLS: {len(ps) - missed} of {len(ps)} plants caught" + ("" if not missed else f"; {missed} MISSED") +
          ("" if not spelled_missed else f"; {spelled_missed} spellings MISSED") +
          ("" if not clean else f"; the unplanted copy itself has {clean} finding(s)"))
    return 0 if missed == 0 and spelled_missed == 0 and clean == 0 else 1


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if any(f not in ("--control",) for f in flags) or len(args) > 1:
        print(__doc__.split("\n\n")[1])
        return 2
    kit = Path(args[0]).resolve() if args else KIT
    if not (kit / "MANIFEST.txt").exists() and not (kit / "START-HERE.md").exists():
        print(f"check_kit: {kit} is not a kit (no MANIFEST.txt, no START-HERE.md)")
        return 2
    return control(kit) if "--control" in flags else run(kit)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:  # a crash is never a verdict (HonestFramework METHOD.md, section 5)
        print(f"check_kit: the gate itself failed, which is no verdict: {type(e).__name__}: {e}")
        sys.exit(3)
