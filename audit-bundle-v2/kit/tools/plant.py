#!/usr/bin/env python3
"""The mechanical half of the planted-fault protocol (WORKFLOW.md, "The planted-fault protocol").

    tools/plant.py make --repo REPO --base BASE --key DRAFT --out COPY [--key-out KEY] [--message TEXT]
        Builds the copy a verifier is given, in round 6's shape: "a fresh repository detached at 9c306e9 (parent
        a30aca5), with no remote, no refs and no route back to P5's own tip" (method/parcelround/archive/
        round6-ledger.zip, lead.md). COPY's objects are one new commit, whose parent is BASE and whose tree is the key's
        real_tip with each plant applied, and the objects that commit reaches: none of the parcel's own commits after
        BASE, and no blob of a planted file's text at real_tip. Into its git directory, make's git commands write HEAD,
        ORIG_HEAD, config, the index (and its shared part, under core.splitIndex), HEAD's reflog, loose objects and
        packs, and no template file of git init's; check --dispatch refuses a file of any other name there. Its work
        tree is its commit checked out. Which commit is the parcel's base is the lead's to give: make prints it, as the
        copy's parent, for the ledger. A plant whose file's text at real_tip is already in BASE's history (a file the
        parcel left as the base had it, restored, or moved unchanged) is refused, since the copy would hold that text. A
        plant on lines the base already had shows them in the copy's diff against BASE, as any change of the parcel's
        does. A copy one of whose objects git fsck --full flags, from the base's history, real_tip's tree or a plant, is
        refused, naming fsck's first complaint, since check would refuse it. The commit takes real_tip's author,
        committer and message, unless --message is given. Then it writes the key with its copy_commit, by default beside
        DRAFT as key-<copy>.json, and prints that file's sha256: the hash goes in the ledger before the verifier is
        dispatched, and the key stays outside every agent's reach until the reveal.
    tools/plant.py hash KEY...
        Prints each key's sha256, in sha256sum's format.
    tools/plant.py check --key KEY --repo REPO [--copy COPY [--dispatch]] [--sha256 HASH]
        Run with --dispatch just before the verifier is dispatched, and without it at the reveal. It holds that the
        key's bytes hash to HASH, when given, and that each plant's old text occurs once in its file when it is applied
        and its new text is not in that file at real_tip. With a copy, it reads the copy's git state: HEAD is detached
        at copy_commit, whose one parent is an ancestor of real_tip and whose tree is real_tip's with the plants
        applied; git fsck --full finds its objects sound, and git count-objects finds no garbage; it has no ref, remote,
        alternates, shallow file, FETCH_HEAD, linked worktree or reflog of a ref, and no *_HEAD at its git directory's
        top and no entry of HEAD's reflog names another commit; check can read every directory of its git directory; and
        of the objects it holds, read by id, none is one its HEAD does not reach, none is a commit of the parcel's after
        the copy's parent, and none is a planted file's text at real_tip. With --dispatch, it also reads what git status
        reports, with untracked and ignored files shown, which must be nothing; the name of each file in its git
        directory, which must be one make writes: the names, not what the files hold; and every directory of its work
        tree, each of which it must be able to read. That is the lead's check against a slip, not a defense against a
        copy built to pass it, since git status trusts the index's flags and stat data and the copy's config. Without
        --dispatch it reads none of these, since a verifier may change its own work tree. Where git will not read REPO
        or the copy as a repository, as when another user owns it, the refusal gives git's own reason. It reads no place
        but the key, the copy and REPO, so the parcel's work elsewhere on the machine is outside it; and it cannot tell
        a wrong base: the parcel's own commits, to it, are those after the copy's parent.
    tools/plant.py list KEY... [--report REPORT]
        Prints each plant. With a report, it also prints the report's lines that name the plant's file or a word
        the plant changed: a reading aid, not a grade. The lead grades each plant caught or missed by reading.
    tools/plant.py selftest
        Builds a repository, a copy, and a case for each refusal, in a temporary directory, and checks them.

A key is round 6's format (that archive's keys/): {"real_tip", "copy_commit", "plants": [{"file", "old", "new",
"shape"}]}. A draft is the same without copy_commit. Plants apply in the key's order, and each one's old text must
occur exactly once in its file when it is applied, its new text nowhere in that file at real_tip. Texts are matched
as UTF-8 bytes, so line endings are part of them. A key may hold no plants: the verifier is told only that the copy
may hold some.

Exit 0 on success; 1 on a refusal, one line naming its reason; 2 on bad usage; 3 if the tool itself failed.
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

PLANT_FIELDS = ("file", "old", "new", "shape")
COMMIT_ID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
# Every file make writes into the copy's git directory, by its path there.
MADE = re.compile(r"HEAD|ORIG_HEAD|config|index|logs/HEAD|objects/[0-9a-f]{2}/(?:[0-9a-f]{38}|[0-9a-f]{62})"
                  r"|objects/pack/pack-(?:[0-9a-f]{40}|[0-9a-f]{64})\.(?:pack|idx|rev)"
                  r"|sharedindex\.(?:[0-9a-f]{40}|[0-9a-f]{64})")      # the last, under core.splitIndex
STOPWORDS = {"the", "and", "for", "its", "not", "with", "that", "this", "from", "are", "was", "has", "but", "all"}


class Refused(Exception):
    pass


class ToolFailed(Exception):
    pass


def git(*args, cwd, data=None, env=None, ok=(0,)):
    r = subprocess.run(["git", *args], cwd=cwd, input=data, capture_output=True, env=env)
    if r.returncode not in ok:
        raise ToolFailed("git %s: exit %d: %s" % (" ".join(args), r.returncode,
                                                   r.stderr.decode("utf-8", "replace").strip()))
    return r


def out(*args, cwd, data=None, env=None):
    return git(*args, cwd=cwd, data=data, env=env).stdout.decode("utf-8").strip()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rmtree(path):
    """shutil.rmtree that also removes the read-only files git writes, which Windows will not delete as they are."""
    def retry(func, p, _exc):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except OSError:
            pass
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=retry)
    else:
        shutil.rmtree(path, onerror=retry)


def inside(path, directory):
    try:
        Path(path).resolve().relative_to(Path(directory).resolve())
        return True
    except ValueError:
        return False


def repository(path):
    """The top of the work tree at path, and its common git directory; refused, with git's own reason, if git will
    not read path as a repository."""
    if not Path(path).is_dir():
        raise Refused("%s is not a directory" % path)
    r = git("rev-parse", "--show-toplevel", "--git-common-dir", cwd=path, ok=(0, 128))
    if r.returncode:
        raise Refused("git will not read %s as a repository: %s" % (path, first_line(r)))
    top, common = r.stdout.decode("utf-8").splitlines()[:2]
    return Path(top).resolve(), (Path(path) / common).resolve() if not os.path.isabs(common) else Path(common).resolve()


def commit_of(repo, rev, what):
    r = git("rev-parse", "--verify", "-q", rev + "^{commit}", cwd=repo, ok=(0, 1, 128))
    if r.returncode:
        raise Refused("%s %s is not a commit in %s" % (what, rev, repo))
    return r.stdout.decode("utf-8").strip()


def load_key(path, final):
    try:
        key = json.loads(Path(path).read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise Refused("%s is not a key: %s" % (path, e))
    want = ("real_tip", "copy_commit", "plants") if final else ("real_tip", "plants")
    if not isinstance(key, dict) or sorted(key) != sorted(want):
        found = sorted(key) if isinstance(key, dict) else type(key).__name__
        raise Refused("%s holds %s; a %s holds exactly %s" % (path, found, "key" if final else "draft", list(want)))
    for field in want[:-1]:
        if not isinstance(key[field], str) or not COMMIT_ID.fullmatch(key[field]):
            raise Refused("%s: %s is not a full commit id" % (path, field))
    if not isinstance(key["plants"], list):
        raise Refused("%s: plants is not a list" % path)
    for i, p in enumerate(key["plants"], 1):
        if not isinstance(p, dict) or sorted(p) != sorted(PLANT_FIELDS):
            raise Refused("%s: plant %d does not hold exactly %s" % (path, i, list(PLANT_FIELDS)))
        if not all(isinstance(p[f], str) for f in PLANT_FIELDS):
            raise Refused("%s: plant %d has a field that is not text" % (path, i))
        if not p["old"] or not p["shape"].strip():
            raise Refused("%s: plant %d has an empty old text or an empty shape" % (path, i))
        if p["old"] == p["new"]:
            raise Refused("%s: plant %d changes nothing" % (path, i))
        parts = p["file"].split("/")
        if p["file"].startswith("/") or "\\" in p["file"] or any(s in ("", ".", "..") for s in parts):
            raise Refused("%s: plant %d's file %r is not a path in the tree" % (path, i, p["file"]))
    return key


def tree(repo, commit):
    """{path: (mode, type, oid)} for every entry of the commit's tree, recursively."""
    raw = git("ls-tree", "-r", "-z", "--full-tree", commit, cwd=repo).stdout
    entries = {}
    for rec in raw.split(b"\0"):
        if rec:
            meta, path = rec.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            entries[path.decode("utf-8", "surrogateescape")] = (mode, kind, oid)
    return entries


def blob(repo, oid):
    return git("cat-file", "blob", oid, cwd=repo).stdout


def planted(repo, key, entries):
    """{file: bytes} for each planted file, the plants applied in order; refused where a plant does not apply."""
    texts = {}
    for i, p in enumerate(key["plants"], 1):
        f = p["file"]
        if f not in texts:
            if f not in entries:
                raise Refused("plant %d: real_tip has no file %s" % (i, f))
            mode, kind, oid = entries[f]
            if kind != "blob" or mode not in ("100644", "100755"):
                raise Refused("plant %d: %s is not a regular file at real_tip (mode %s)" % (i, f, mode))
            twins = sorted(q for q, e in entries.items() if q != f and e[2] == oid)
            if twins:
                raise Refused("plant %d: %s holds the same text as %s at real_tip, so the copy would hold the "
                              "unplanted text: plant another file" % (i, f, twins[0]))
            texts[f] = blob(repo, oid)
        old, new = p["old"].encode("utf-8"), p["new"].encode("utf-8")
        if new and new in blob(repo, entries[f][2]):
            raise Refused("plant %d: %s already holds its new text at real_tip, so the plant could not be told "
                          "from the parcel's own text" % (i, f))
        n = texts[f].count(old)
        if n != 1:
            raise Refused("plant %d: its old text occurs %d times in %s when it is applied (it must occur once)"
                          % (i, n, f))
        texts[f] = texts[f].replace(old, new, 1)
    for f, data in texts.items():
        if data == blob(repo, entries[f][2]):
            raise Refused("the plants on %s cancel out" % f)
    return texts


def identity_env(repo, commit):
    fields = out("log", "-1", "--date=raw", "--format=%an%x00%ae%x00%ad%x00%cn%x00%ce%x00%cd", commit,
                 cwd=repo).split("\0")
    env = dict(os.environ)
    for name, value in zip(("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE",
                            "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL", "GIT_COMMITTER_DATE"), fields):
        env[name] = value
    return env


def expected_tree(repo, entries, texts):
    """The copy's entries: real_tip's, with each planted file's blob id replaced."""
    want = dict(entries)
    for f, data in texts.items():
        mode, kind, _ = entries[f]
        want[f] = (mode, kind, out("hash-object", "--no-filters", "--stdin", cwd=repo, data=data))
    return want


def route_back(copy, repo, base, real_tip):
    """The parcel's own commits that the copy holds: real_tip, and every commit from base to it."""
    own = out("rev-list", "%s..%s" % (base, real_tip), cwd=repo).split()
    r = git("cat-file", "--batch-check", cwd=copy, data=("\n".join(own) + "\n").encode())
    return [line.split()[0] for line in r.stdout.decode().splitlines() if not line.endswith(" missing")]


def unreachable(copy):
    """The objects the copy holds that its HEAD does not reach."""
    held = out("cat-file", "--batch-all-objects", "--batch-check=%(objectname)", cwd=copy).split()
    reached = set(out("rev-list", "--objects", "--no-object-names", "HEAD", cwd=copy).split())
    return sorted(set(held) - reached)


def first_line(r):
    """The first line git wrote to stderr, or its exit code."""
    return (r.stderr.decode("utf-8", "replace").strip().splitlines() or ["exit %d" % r.returncode])[0]


def listing(top, skip_git=False):
    """(each file under top, by its path there, a link counting as a file; each directory under it that cannot be
    read). With skip_git, top's own .git is left out."""
    files, unread = [], []

    def failed(e):
        unread.append(Path(e.filename).relative_to(top).as_posix() if e.filename else ".")
    for d, dirs, names in os.walk(top, onerror=failed):
        if skip_git and Path(d) == Path(top):
            dirs[:] = [x for x in dirs if x != ".git"]
        for name in names + dirs:
            q = os.path.join(d, name)
            if os.path.islink(q) or not os.path.isdir(q):
                files.append(Path(q).relative_to(top).as_posix())
    return sorted(files), sorted(unread)


def unmade(gitdir, files):
    """The files of a git directory that make does not write: any but HEAD, ORIG_HEAD, config, the index (and its
    shared part, under core.splitIndex), HEAD's reflog, loose objects and packs. A link counts, wherever it points."""
    return [f for f in files if os.path.islink(os.path.join(gitdir, f)) or not MADE.fullmatch(f)]


def copy_problems(copy, repo, key, want, originals, dispatch=False):
    """What makes the copy at COPY other than the key says it is. originals: {blob id: file} of each planted file's
    text at real_tip. With dispatch, also what makes it other than make left it: its work tree and index, and every
    file of its git directory."""
    problems = []
    r = git("rev-parse", "--verify", "-q", "HEAD", cwd=copy, ok=(0, 1, 128))
    if r.returncode == 128:
        problems.append("git will not read the copy: %s" % first_line(r))
        return problems
    head = r.stdout.decode().strip()
    if head != key["copy_commit"]:
        problems.append("the copy's HEAD is %s, not the key's copy_commit %s" % (head or "missing", key["copy_commit"]))
        return problems
    if git("symbolic-ref", "-q", "HEAD", cwd=copy, ok=(0, 1)).returncode == 0:
        problems.append("the copy's HEAD is on a branch, not detached")
    refs = out("for-each-ref", "--format=%(refname)", cwd=copy).split()
    if refs:
        problems.append("the copy holds refs: %s" % ", ".join(refs[:5]))
    remotes = out("remote", cwd=copy).split()
    if remotes:
        problems.append("the copy has remotes: %s" % ", ".join(remotes))
    gitdir = Path(out("rev-parse", "--absolute-git-dir", cwd=copy))
    gitfiles, unread = listing(gitdir)
    if unread:
        problems.append("check cannot read %d director%s of the copy's git directory, %s first"
                        % (len(unread), "y" if len(unread) == 1 else "ies", unread[0]))
    if (gitdir / "objects" / "info" / "alternates").exists():
        problems.append("the copy borrows objects from another repository (objects/info/alternates)")
    if (gitdir / "shallow").exists():
        problems.append("the copy's history is shallow")
    if (gitdir / "FETCH_HEAD").exists():
        problems.append("the copy has a FETCH_HEAD: something was fetched into it")
    for other in sorted(gitdir.glob("*_HEAD")):
        if other.name != "FETCH_HEAD" and set(other.read_text(errors="replace").split()) - {head}:
            problems.append("the copy's %s names something other than its own commit" % other.name)
    linked = sorted(p.name for p in (gitdir / "worktrees").iterdir()) if (gitdir / "worktrees").is_dir() else []
    if linked:
        problems.append("the copy has a linked worktree (worktrees/%s)" % linked[0])
    if (gitdir / "logs" / "refs").exists() and any(q.is_file() for q in (gitdir / "logs" / "refs").rglob("*")):
        problems.append("the copy holds reflogs of refs (logs/refs/)")
    logged = set()
    if (gitdir / "logs" / "HEAD").is_file():
        for entry in (gitdir / "logs" / "HEAD").read_text(errors="replace").splitlines():
            logged.update(entry.split("\t", 1)[0].split()[:2])
    logged -= {head, "0" * len(head)}
    if logged:
        problems.append("the copy's HEAD reflog names other commits: %s" % ", ".join(sorted(logged)[:3]))
    if dispatch:
        _, unread = listing(copy, skip_git=True)
        if unread:
            problems.append("check cannot read %d director%s of the copy's work tree, %s first"
                            % (len(unread), "y" if len(unread) == 1 else "ies", unread[0]))
        extra = unmade(gitdir, gitfiles)
        if extra:
            problems.append("the copy's git directory holds %d file%s make does not write: %s"
                            % (len(extra), "" if len(extra) == 1 else "s", ", ".join(extra[:5])))
        st = git("-c", "core.fsmonitor=false", "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignored",
                 cwd=copy, ok=tuple(range(256)))
        status = [e for e in st.stdout.decode("utf-8", "replace").split("\0") if e]
        if st.returncode:
            problems.append("git status fails in the copy: %s" % first_line(st))
        elif status:
            problems.append("git status reports %d path%s in the copy, the first %r"
                            % (len(status), "" if len(status) == 1 else "s", status[0]))
    fsck = git("fsck", "--full", "--no-dangling", "--no-progress", cwd=copy, ok=tuple(range(256)))
    if fsck.returncode:
        said = (fsck.stderr + fsck.stdout).decode("utf-8", "replace").strip().splitlines()
        said = said or ["exit %d" % fsck.returncode]
        problems.append("git fsck --full refuses the copy's objects: %s" % said[0])
    counted = git("count-objects", "-v", cwd=copy)
    garbage = re.search(r"^garbage: ([0-9]+)$", counted.stdout.decode("utf-8", "replace"), re.M)
    if not garbage or garbage.group(1) != "0":
        warned = counted.stderr.decode("utf-8", "replace").strip().splitlines()
        problems.append("the copy's objects/ holds files git reads as neither a loose object nor a pack (garbage %s)%s"
                        % (garbage.group(1) if garbage else "not reported", ": " + warned[0] if warned else ""))
    stray = unreachable(copy)
    if stray:
        problems.append("the copy holds %d object%s its HEAD does not reach, %s among them"
                        % (len(stray), "" if len(stray) == 1 else "s", stray[0]))
    have = git("cat-file", "--batch-check", cwd=copy, data="".join(o + "\n" for o in sorted(originals)).encode())
    for line in have.stdout.decode().splitlines():
        if not line.endswith(" missing"):
            oid = line.split()[0]
            problems.append("the copy holds the unplanted text of %s, as blob %s" % (originals[oid], oid))
    parents = out("rev-list", "--parents", "-n", "1", head, cwd=copy).split()[1:]
    if len(parents) != 1:
        problems.append("the copy's commit has %d parents, not one" % len(parents))
        return problems
    base = parents[0]
    if git("merge-base", "--is-ancestor", base, key["real_tip"], cwd=repo, ok=(0, 1, 128)).returncode:
        problems.append("the copy's parent %s is not an ancestor of real_tip" % base)
        return problems
    held = route_back(copy, repo, base, key["real_tip"])
    if held:
        problems.append("the copy holds %d of the parcel's own commits, %s among them" % (len(held), held[0]))
    got = tree(copy, head)
    differ = sorted(p for p in set(got) | set(want) if got.get(p) != want.get(p))
    if differ:
        problems.append("the copy's tree differs from real_tip with the plants in %d paths: %s"
                        % (len(differ), ", ".join(differ[:8])))
    return problems


def cmd_make(a):
    repo, out_dir, draft = Path(a.repo).resolve(), Path(a.out).resolve(), Path(a.key).resolve()
    top, common = repository(repo)
    if out("rev-parse", "--is-shallow-repository", cwd=repo) == "true":
        raise Refused("%s is a shallow repository: its copy's history would be cut; deepen it first" % top)
    key = load_key(draft, final=False)
    real_tip = commit_of(repo, key["real_tip"], "real_tip")
    base = commit_of(repo, a.base, "the base")
    if real_tip == base:
        raise Refused("real_tip is the base: the parcel's work has no commit of its own")
    if git("merge-base", "--is-ancestor", base, real_tip, cwd=repo, ok=(0, 1)).returncode:
        raise Refused("the base %s is not an ancestor of real_tip %s" % (base, real_tip))
    if out_dir.exists() and (not out_dir.is_dir() or any(out_dir.iterdir())):
        raise Refused("%s is not an empty directory" % out_dir)
    places = ((top, "the parcel's repository"), (common, "the parcel's git directory"))
    for place, what in places:
        if inside(out_dir, place):
            raise Refused("the copy %s would be inside %s, %s" % (out_dir, what, place))
    key_out = Path(a.key_out).resolve() if a.key_out else None
    for k in [draft] + ([key_out] if key_out else []):
        for place, what in places + ((out_dir, "the copy"),):
            if inside(k, place):
                raise Refused("the key %s is inside %s, %s: keep it outside every agent's reach" % (k, what, place))
    if key_out and key_out.exists():
        raise Refused("%s is already there, and a key is never replaced" % key_out)
    entries = tree(repo, real_tip)
    texts = planted(repo, key, entries)
    want = expected_tree(repo, entries, texts)
    originals = {entries[f][2]: f for f in texts}
    message = a.message.encode("utf-8") if a.message is not None else \
        git("log", "-1", "--format=%B", real_tip, cwd=repo).stdout
    env = identity_env(repo, real_tip)
    made = not out_dir.exists()
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        fmt = out("rev-parse", "--show-object-format", cwd=repo)
        git("init", "-q", "--template=", "--object-format=" + fmt, str(out_dir), cwd=out_dir)
        git("index-pack", "--stdin", cwd=out_dir,
            data=git("pack-objects", "--revs", "--stdout", "-q", cwd=repo, data=(base + "\n").encode()).stdout)
        in_base = git("cat-file", "--batch-check", cwd=out_dir,
                      data="".join(o + "\n" for o in sorted(originals)).encode()).stdout.decode().splitlines()
        held = sorted(originals[l.split()[0]] for l in in_base if not l.endswith(" missing"))
        if held:
            raise Refused("%s's text at real_tip is in the base's history (the parcel left it as the base had it, "
                          "restored it, or moved it unchanged), so the copy would hold the unplanted text: plant in "
                          "a file whose text the parcel changed" % held[0])
        have = git("cat-file", "--batch-check", cwd=out_dir,
                   data="".join(oid + "\n" for _, kind, oid in entries.values() if kind != "commit").encode())
        missing = [l.split()[0] for l in have.stdout.decode().splitlines() if l.endswith(" missing")]
        missing = [oid for oid in missing if oid not in originals]
        if missing:
            git("index-pack", "--stdin", cwd=out_dir,
                data=git("pack-objects", "--stdout", "-q", cwd=repo,
                         data="".join(m + "\n" for m in missing).encode()).stdout)
        for f, data in texts.items():
            oid = out("hash-object", "-w", "--no-filters", "--stdin", cwd=out_dir, data=data)
            if oid != want[f][2]:
                raise ToolFailed("the planted %s hashed to %s in the copy and %s in the repository"
                                 % (f, oid, want[f][2]))
        index = b"".join(("%s %s\t" % (mode, oid)).encode() + p.encode("utf-8", "surrogateescape") + b"\0"
                         for p, (mode, _, oid) in sorted(want.items()))
        git("update-index", "-z", "--index-info", cwd=out_dir, data=index)
        new_tree = out("write-tree", cwd=out_dir)
        copy = out("commit-tree", new_tree, "-p", base, "--no-gpg-sign", cwd=out_dir, data=message, env=env)
        git("update-ref", "--no-deref", "-m", "plant.py: the copy", "HEAD", copy, cwd=out_dir, env=env)
        git("-c", "core.fsmonitor=false", "reset", "-q", "--hard", "HEAD", cwd=out_dir, env=env)
        final = {"real_tip": real_tip, "copy_commit": copy, "plants": key["plants"]}
        problems = copy_problems(out_dir, repo, final, want, originals)
        flagged = [p for p in problems if p.startswith("git fsck --full refuses")]
        if flagged:
            raise Refused("%s: the copy holds the base's history and real_tip's tree with the plants applied, and git "
                          "fsck flags one of their objects, so make cannot build a copy check would pass" % flagged[0])
        if problems:
            raise ToolFailed("the copy is not what it should be: " + "; ".join(problems))
        if key_out is None:
            key_out = draft.parent / ("key-%s.json" % copy[:7])
            if key_out.exists():
                raise Refused("%s is already there, and a key is never replaced" % key_out)
    except BaseException:
        rmtree(out_dir)
        if not made:
            out_dir.mkdir(exist_ok=True)
        raise
    key_out.write_bytes((json.dumps(final, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    dirty = out("-c", "core.fsmonitor=false", "status", "--porcelain", cwd=out_dir)
    n, m = len(key["plants"]), len(texts)
    print("copy %s: detached at %s (parent %s); %d plant%s in %d file%s"
          % (out_dir, copy, base, n, "" if n == 1 else "s", m, "" if m == 1 else "s"))
    print("key %s" % key_out)
    print("key sha256 %s" % sha256(key_out))
    if dirty:
        print("note: the copy's work tree differs from its commit in %d paths after checkout, by this machine's "
              "git settings (line endings or filters); its commit is exact, but check --dispatch refuses its work "
              "tree" % len(dirty.splitlines()))


def cmd_hash(a):
    for k in a.keys:
        if not Path(k).is_file():
            raise Refused("%s is not a file" % k)
        print("%s  %s" % (sha256(k), k))


def cmd_check(a):
    key_path, repo = Path(a.key), Path(a.repo).resolve()
    if not key_path.is_file():
        raise Refused("%s is not a file" % key_path)
    digest = sha256(key_path)
    if a.sha256 and digest != a.sha256.strip().lower():
        raise Refused("the key's sha256 is %s, not the recorded %s" % (digest, a.sha256.strip().lower()))
    key = load_key(key_path, final=True)
    repository(repo)
    commit_of(repo, key["real_tip"], "real_tip")
    entries = tree(repo, key["real_tip"])
    texts = planted(repo, key, entries)
    want = expected_tree(repo, entries, texts)
    said = ["key sha256 %s%s" % (digest, ", as recorded" if a.sha256 else ""),
            "%d plants: each old text occurs once in its file when it is applied, and each new text is not in its "
            "file at real_tip" % len(key["plants"])]
    if a.dispatch and not a.copy:
        raise Refused("--dispatch reads a copy: give it --copy")
    if a.copy and not Path(a.copy).is_dir():
        raise Refused("the copy %s is not a directory" % a.copy)
    if a.copy:
        problems = copy_problems(Path(a.copy).resolve(), repo, key, want, {entries[f][2]: f for f in texts},
                                 dispatch=a.dispatch)
        if problems:
            raise Refused("; ".join(problems))
        said.append("the copy's git state: HEAD is detached at copy_commit, whose one parent is an ancestor of "
                    "real_tip and whose tree is real_tip's with the plants applied; git fsck --full finds its objects "
                    "sound and git count-objects no garbage; it has no ref, remote, alternates, shallow file, "
                    "FETCH_HEAD, linked worktree or reflog of a ref, and no *_HEAD at its git directory's top and no "
                    "entry of HEAD's reflog names another commit; check read every directory of its git directory; "
                    "and of its objects, read by id, none is one HEAD "
                    "does not reach, none is a commit of the parcel's after the copy's parent, and none is a planted "
                    "file's text at real_tip")
        said.append("for the dispatch, git status, with untracked and ignored files shown, reports nothing, each file "
                    "in its git directory has a name make writes, and check read every directory of its work tree"
                    if a.dispatch else
                    "its work tree and its git directory's other files were not read: --dispatch reads them")
    print("check: " + "; ".join(said))


def changed_words(old, new):
    a, b = re.findall(r"\w+", old), re.findall(r"\w+", new)
    words = set()
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op != "equal":
            words.update(a[i1:i2])
            words.update(b[j1:j2])
    return sorted(w for w in words if (w.isdigit() or len(w) >= 3) and w.lower() not in STOPWORDS)


def cmd_list(a):
    report = None
    if a.report:
        try:
            report = Path(a.report).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as e:
            raise Refused("cannot read the report %s: %s" % (a.report, e))
    for k in a.keys:
        key = load_key(k, final=True)
        print("key %s, sha256 %s: real_tip %s, copy %s" % (k, sha256(k), key["real_tip"], key["copy_commit"]))
        if report is not None:
            named = any(key["copy_commit"][:7] in line for line in report)
            print("  the report %s the copy's commit %s" % ("names" if named else "does NOT name",
                                                          key["copy_commit"][:7]))
        for i, p in enumerate(key["plants"], 1):
            print("  plant %d, %s: %s" % (i, p["file"], p["shape"]))
            print("    old: %s" % json.dumps(p["old"], ensure_ascii=False))
            print("    new: %s" % json.dumps(p["new"], ensure_ascii=False))
            if report is not None:
                words = changed_words(p["old"], p["new"])
                pat = re.compile(r"(?i)" + "|".join([re.escape(p["file"])] +
                                                    [r"(?<!\w)%s(?!\w)" % re.escape(w) for w in words]))
                hits = [(n, line) for n, line in enumerate(report, 1) if pat.search(line)]
                print("    report lines naming %s or a changed word (%s): %d" % (p["file"], ", ".join(words),
                                                                                 len(hits)))
                for n, line in hits[:12]:
                    print("      %d: %s" % (n, line.strip()[:200]))
    print("This list is not a grade: grade each plant caught or missed by reading the report.")


def selftest(_a):
    me = [sys.executable, "-I", str(Path(__file__).resolve())]
    t = Path(tempfile.mkdtemp(prefix="plant-selftest-"))
    checks = failed = 0
    try:
        gitconfig = t / "gitconfig"
        gitconfig.write_text("[init]\n\tdefaultBranch = main\n")
        env = dict(os.environ, GIT_CONFIG_GLOBAL=str(gitconfig), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="selftest", GIT_AUTHOR_EMAIL="selftest@example.invalid",
                   GIT_COMMITTER_NAME="selftest", GIT_COMMITTER_EMAIL="selftest@example.invalid")

        def sh(*args, cwd, data=None):
            r = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, input=data)
            if r.returncode:
                raise ToolFailed("selftest setup: git %s: %s" % (" ".join(args), r.stderr.decode()))
            return r.stdout.decode().strip()

        def run(*args, extra=None):
            r = subprocess.run(me + [str(x) for x in args], env=dict(env, **(extra or {})), capture_output=True)
            return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")

        def check(cond, what):
            nonlocal checks, failed
            checks += 1
            if not cond:
                failed += 1
                print("FAIL: " + what)

        def refused(reason, *args):
            rc, so, se = run(*args)
            check(rc == 1 and se.startswith("plant.py: refused: ") and reason in se,
                  "want exit 1 naming %r, got exit %d: %s" % (reason, rc, (se or so).strip()))

        def held(copy):
            return set(sh("cat-file", "--batch-all-objects", "--batch-check=%(objectname)", cwd=copy).split())

        repo = t / "repo"
        repo.mkdir()
        sh("init", "-q", cwd=repo)
        (repo / "docs").mkdir()
        (repo / "README.md").write_bytes(b"hello\n")
        (repo / "docs" / "x.md").write_bytes(b"alpha beta gamma\nline two\nline three\n")
        (repo / "tool.sh").write_bytes(b"echo hi\n")
        (repo / "tool.sh").chmod(0o755)
        sh("add", "-A", cwd=repo)
        sh("update-index", "--chmod=+x", "tool.sh", cwd=repo)
        sh("commit", "-q", "-m", "base", cwd=repo)
        base = sh("rev-parse", "HEAD", cwd=repo)
        (repo / "docs" / "x.md").write_bytes(b"alpha beta gamma\nline two\nline three\nfour\n")
        (repo / "new.md").write_bytes(b"the count is 5 of 38 entries\r\nsecond line\r\n")
        sh("add", "-A", cwd=repo)
        sh("commit", "-q", "-m", "the parcel's first commit", cwd=repo)
        middle = sh("rev-parse", "HEAD", cwd=repo)
        (repo / "new.md").write_bytes(b"the count is 5 of 38 entries\r\nsecond line, changed\r\n")
        sh("commit", "-q", "-am", "the parcel's tip", cwd=repo)
        tip = sh("rev-parse", "HEAD", cwd=repo)
        sh("checkout", "-q", "-b", "side", base, cwd=repo)
        (repo / "side.md").write_bytes(b"side\n")
        sh("add", "-A", cwd=repo)
        sh("commit", "-q", "-m", "a side commit", cwd=repo)
        side = sh("rev-parse", "HEAD", cwd=repo)
        sh("checkout", "-q", "main", cwd=repo)
        originals = {sh("rev-parse", "%s:%s" % (tip, f), cwd=repo) for f in ("new.md", "docs/x.md")}

        lead = t / "lead"
        lead.mkdir()

        def draft(name, plants, real_tip=tip, extra=None, raw=None):
            p = lead / name
            if raw is not None:
                p.write_text(raw)
                return p
            d = {"real_tip": real_tip, "plants": plants}
            d.update(extra or {})
            p.write_text(json.dumps(d, indent=2))
            return p

        good = [{"file": "new.md", "old": "5 of 38", "new": "5 of 28", "shape": "a figure transcribed wrong"},
                {"file": "docs/x.md", "old": "beta", "new": "delta", "shape": "a word changed"}]
        d = draft("draft.json", good)
        copy = t / "copy"
        rc, so, se = run("make", "--repo", repo, "--base", base, "--key", d, "--out", copy)
        check(rc == 0, "make: exit %d: %s" % (rc, se.strip()))
        if rc == 0:
            key = Path(re.search(r"^key (.+)$", so, re.M).group(1))
            printed = re.search(r"^key sha256 ([0-9a-f]{64})$", so, re.M).group(1)
            check(printed == sha256(key), "make prints the key's sha256")
            k = json.loads(key.read_text())
            check(list(k) == ["real_tip", "copy_commit", "plants"] and k["plants"] == good, "the key's format")
            c = k["copy_commit"]
            check(sh("rev-parse", "HEAD", cwd=copy) == c, "the copy's HEAD is the key's copy_commit")
            check(subprocess.run(["git", "symbolic-ref", "-q", "HEAD"], cwd=copy, env=env).returncode == 1,
                  "the copy's HEAD is detached")
            check(sh("for-each-ref", cwd=copy) == "" and sh("remote", cwd=copy) == "", "no refs, no remotes")
            check(sh("rev-parse", "HEAD^", cwd=copy) == base, "the copy's parent is the base")
            for oid in (tip, middle):
                check(oid not in held(copy), "the copy holds none of the parcel's own commits (%s)" % oid[:7])
            check(not (originals & held(copy)), "the copy holds no planted file's unplanted text")
            reached = set(sh("rev-list", "--objects", "--no-object-names", "HEAD", cwd=copy).split())
            check(held(copy) == reached, "the copy holds no object its HEAD does not reach")
            check("note:" not in so, "no note for plants in files the parcel changed")
            check((copy / "new.md").read_bytes() == b"the count is 5 of 28 entries\r\nsecond line, changed\r\n",
                  "the plant applied, its line endings kept")
            check((copy / "docs" / "x.md").read_bytes() == b"alpha delta gamma\nline two\nline three\nfour\n",
                  "the second plant applied")
            diff = sh("diff", "--name-only", base, "HEAD", cwd=copy).split()
            check(sorted(diff) == ["docs/x.md", "new.md"], "the copy differs from the base in the parcel's files")
            check("100755 blob" in sh("ls-tree", "HEAD", "tool.sh", cwd=copy), "a file's mode is kept")
            rc, so2, se2 = run("check", "--key", key, "--repo", repo, "--copy", copy, "--sha256", printed)
            check(rc == 0 and "were not read: --dispatch reads them" in so2,
                  "check passes on the copy make built, saying what it did not read: %s" % (se2 or so2).strip())
            rc, so2, se2 = run("check", "--key", key, "--repo", repo, "--copy", copy, "--dispatch")
            check(rc == 0 and "for the dispatch" in so2, "check --dispatch passes on the copy make built: %s"
                  % (se2 or so2).strip())
            check(not any((copy / ".git" / x).exists() for x in ("hooks", "description", "info")),
                  "make writes none of git init's template files into the copy")
            refused("--dispatch reads a copy", "check", "--key", key, "--repo", repo, "--dispatch")
            refused("not the recorded", "check", "--key", key, "--repo", repo, "--sha256", "0" * 64)
            tampered = lead / "tampered.json"
            tampered.write_bytes(key.read_bytes().replace(b"a word changed", b"a word changed!"))
            refused("not the recorded", "check", "--key", tampered, "--repo", repo, "--sha256", printed)
            report = lead / "report.md"
            report.write_text("## findings\n1. new.md says 5 of 28; its source says 38.\n2. nothing else\n")
            rc, so3, _ = run("list", key, "--report", report)
            check(rc == 0 and "2: 1. new.md says 5 of 28" in so3 and "does NOT name" in so3 and "not a grade" in so3,
                  "list sets the report's lines beside each plant")
            refused("cannot read the report", "list", key, "--report", lead / "absent.md")
            rc, so4, _ = run("hash", key)
            check(rc == 0 and so4.split()[0] == printed, "hash prints the key's sha256")
            refused("is not a file", "hash", lead / "absent.json")
            refused("is not a file", "check", "--key", lead / "absent.json", "--repo", repo)

            def fresh(name):
                """Another copy of the same draft, which is the same commit, with its own key file."""
                cp, kp = t / name, lead / (name + ".json")
                rc, _, se = run("make", "--repo", repo, "--base", base, "--key", d, "--out", cp, "--key-out", kp)
                check(rc == 0 and json.loads(kp.read_text())["copy_commit"] == c,
                      "the same draft makes the same copy commit: %s" % se.strip())
                return cp, kp

            def refused_copy(reason, name, spoil, key_from=None, dispatch=False):
                cp, kp = fresh(name)
                spoil(cp)
                if key_from is not None:
                    kp.write_text(json.dumps(dict(k, copy_commit=key_from(cp)), indent=2))
                refused(reason, "check", "--key", kp, "--repo", repo, "--copy", cp,
                        *(["--dispatch"] if dispatch else []))
                return cp, kp

            def passes_unless_dispatch(cp, kp, what):
                rc, _, se = run("check", "--key", kp, "--repo", repo, "--copy", cp)
                check(rc == 0, "without --dispatch, check does not read %s: %s" % (what, se.strip()))

            refused_copy("holds 2 of the parcel's own commits", "fetched",
                         lambda cp: sh("fetch", "-q", str(repo), "main", cwd=cp))
            refused_copy("has a FETCH_HEAD", "fetched2", lambda cp: sh("fetch", "-q", str(repo), "main", cwd=cp))
            refused_copy("1 object its HEAD does not reach", "stray",
                         lambda cp: sh("hash-object", "-w", "--stdin", cwd=cp, data=b"the unplanted text\n"))
            refused_copy("alternates", "alternates", lambda cp: (cp / ".git" / "objects" / "info" / "alternates")
                         .write_text(str((repo / ".git" / "objects").resolve()) + "\n"))
            refused_copy("on a branch, not detached", "branch", lambda cp: sh("checkout", "-q", "-b", "x", cwd=cp))
            refused_copy("holds refs: refs/tags/t", "tagged", lambda cp: sh("update-ref", "refs/tags/t", "HEAD",
                                                                            cwd=cp))
            refused_copy("has remotes: o", "remote", lambda cp: sh("remote", "add", "o", "https://example.invalid/x",
                                                                   cwd=cp))
            refused_copy("is shallow", "shallow", lambda cp: (cp / ".git" / "shallow").write_text(base + "\n"))
            refused_copy("ORIG_HEAD names something other", "orig", lambda cp: (cp / ".git" / "ORIG_HEAD")
                         .write_text(base + "\n"))
            def reflog_of_a_ref(cp):
                (cp / ".git" / "logs" / "refs" / "heads").mkdir(parents=True, exist_ok=True)
                (cp / ".git" / "logs" / "refs" / "heads" / "gone").write_text(
                    "%s %s selftest <selftest@example.invalid> 0 +0000\tbranch: gone\n" % ("0" * 40, tip))
            refused_copy("reflogs of refs", "reflogged", reflog_of_a_ref)
            unplanted = b"the count is 5 of 38 entries\r\nsecond line, changed\r\n"
            refused_copy("the unplanted text of new.md", "unplanted", lambda cp: sh(
                "hash-object", "-w", "--stdin", cwd=cp, data=unplanted))

            def swap_object(cp):
                """The planted blob's loose object rewritten to hold the unplanted text, under the planted id."""
                mine, theirs = sh("rev-parse", "HEAD:new.md", cwd=cp), sh("rev-parse", "%s:new.md" % tip, cwd=repo)
                path = cp / ".git" / "objects" / mine[:2] / mine[2:]
                path.chmod(0o644)
                path.write_bytes((repo / ".git" / "objects" / theirs[:2] / theirs[2:]).read_bytes())
            refused_copy("git fsck --full refuses the copy's objects", "swapped", swap_object)

            def unindexed_pack(cp):
                """A pack of the unplanted blob in objects/pack/, with no index beside it."""
                name = sh("pack-objects", "-q", str(t / "unindexed"), cwd=repo,
                          data=(sh("rev-parse", "%s:new.md" % tip, cwd=repo) + "\n").encode())
                shutil.copy(t / ("unindexed-%s.pack" % name),
                            cp / ".git" / "objects" / "pack" / ("pack-%s.pack" % name))
            refused_copy("neither a loose object nor a pack (garbage 1)", "unindexed", unindexed_pack)
            refused_copy("has a linked worktree (worktrees/copy-worktree)", "worktreed", lambda cp: sh(
                "worktree", "add", "-q", "--detach", str(t / "copy-worktree"), "HEAD", cwd=cp))
            passes_unless_dispatch(*refused_copy(
                "git status reports 1 path in the copy, the first ' M new.md'", "restored",
                lambda cp: (cp / "new.md").write_bytes(unplanted), dispatch=True), "the work tree")
            refused_copy("git status reports 1 path in the copy, the first '?? notes.json'", "keyed",
                         lambda cp: shutil.copy(key, cp / "notes.json"), dispatch=True)

            def ignored(cp):
                (t / "excludes").write_text("*.log\n")
                sh("config", "core.excludesFile", str(t / "excludes"), cwd=cp)
                (cp / "run.log").write_bytes(unplanted)
            refused_copy("git status reports 1 path in the copy, the first '!! run.log'", "ignored", ignored,
                         dispatch=True)
            passes_unless_dispatch(*refused_copy(
                "git directory holds 1 file make does not write: MERGE_MSG", "merging",
                lambda cp: (cp / ".git" / "MERGE_MSG").write_bytes(unplanted), dispatch=True),
                "the git directory's other files")
            refused_copy("git status fails in the copy", "bare", lambda cp: sh("config", "core.bare", "true", cwd=cp),
                         dispatch=True)
            refused_copy("git will not read the copy: ", "unreadable-config",
                         lambda cp: (cp / ".git" / "config").write_bytes(b"[[[ not a config\n"))
            refused("the copy %s is not a directory" % (t / "absent"), "check", "--key", key, "--repo", repo,
                    "--copy", t / "absent")
            cp, _ = fresh("unreadable")
            (cp / "secret").mkdir()
            (cp / "secret" / "notes.md").write_bytes(unplanted)
            (cp / ".git" / "hidden").mkdir()
            (cp / ".git" / "hidden" / "MERGE_MSG").write_bytes(unplanted)
            entries = tree(repo, tip)
            texts = planted(repo, k, entries)
            real_scandir, saved_env = os.scandir, os.environ.copy()

            def scandir(path="."):
                """os.scandir as a user who cannot read the two directories meets it: root reads every one."""
                if os.path.basename(os.fspath(path)) in ("secret", "hidden"):
                    raise PermissionError(13, "Permission denied", os.fspath(path))
                return real_scandir(path)
            os.scandir = scandir
            os.environ.update(env)
            try:
                got = copy_problems(cp.resolve(), repo, k, expected_tree(repo, entries, texts),
                                    {entries[f][2]: f for f in texts}, dispatch=True)
            finally:
                os.scandir = real_scandir
                os.environ.clear()
                os.environ.update(saved_env)
            check(any("cannot read 1 directory of the copy's git directory, hidden first" in g for g in got),
                  "check refuses a directory of the git directory it cannot read: %s" % got)
            check(any("cannot read 1 directory of the copy's work tree, secret first" in g for g in got),
                  "check --dispatch refuses a directory of the work tree it cannot read: %s" % got)
            split = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.splitIndex", "GIT_CONFIG_VALUE_0": "true"}
            rc, _, se = run("make", "--repo", repo, "--base", base, "--key", d, "--out", t / "split",
                            "--key-out", lead / "split.json", extra=split)
            rc2, _, se2 = run("check", "--key", lead / "split.json", "--repo", repo, "--copy", t / "split",
                              "--dispatch", extra=split)
            shared = rc == 0 and any(q.name.startswith("sharedindex.") for q in (t / "split" / ".git").iterdir())
            check(shared and rc2 == 0, "under core.splitIndex, check --dispatch passes the copy make left, a shared "
                  "index among its files: %s" % (se or se2).strip())

            def move_head(cp, *parents):
                commit = sh("commit-tree", sh("rev-parse", "HEAD^{tree}", cwd=cp), *parents, "-m", "x", cwd=cp)
                sh("update-ref", "--no-deref", "HEAD", commit, cwd=cp)
                return commit

            refused_copy("not the key's copy_commit", "moved", lambda cp: move_head(cp, "-p", base))
            refused_copy("reflog names other commits", "relogged", lambda cp: move_head(cp, "-p", base),
                         key_from=lambda cp: sh("rev-parse", "HEAD", cwd=cp))
            refused_copy("has 2 parents, not one", "merged",
                         lambda cp: move_head(cp, "-p", base, "-p", move_head(cp, "-p", base)),
                         key_from=lambda cp: sh("rev-parse", "HEAD", cwd=cp))
            refused_copy("is not an ancestor of real_tip", "unrelated",
                         lambda cp: move_head(cp, "-p", move_head(cp, "-p", base)),
                         key_from=lambda cp: sh("rev-parse", "HEAD", cwd=cp))

            def edit_readme(cp):
                (cp / "README.md").write_bytes(b"hello, changed\n")
                sh("add", "README.md", cwd=cp)
                commit = sh("commit-tree", sh("write-tree", cwd=cp), "-p", base, "-m", "x", cwd=cp)
                sh("update-ref", "--no-deref", "HEAD", commit, cwd=cp)

            refused_copy("differs from real_tip with the plants in 1 paths: README.md", "edited", edit_readme,
                         key_from=lambda cp: sh("rev-parse", "HEAD", cwd=cp))
            refused("is already there", "make", "--repo", repo, "--base", base, "--key", d, "--out", t / "copy2",
                    "--key-out", key)
            check(not (t / "copy2").exists(), "a refused make leaves no copy")
            refused("is already there", "make", "--repo", repo, "--base", base, "--key", d, "--out", t / "copy2")
            check(not (t / "copy2").exists(), "a make refused for its default key's name leaves no copy")
        refused("is not an empty directory", "make", "--repo", repo, "--base", base, "--key", d, "--out", copy)
        refused("occurs 0 times", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d1.json", [dict(good[0], old="5 of 39")]))
        refused("occurs 2 times", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d2.json", [{"file": "docs/x.md", "old": "line", "new": "LINE", "shape": "s"}]))
        refused("already holds its new text", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d3.json", [{"file": "docs/x.md", "old": "alpha", "new": "gamma", "shape": "s"}]))
        refused("changes nothing", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d4.json", [dict(good[0], new="5 of 38")]))
        refused("has no file", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d5.json", [dict(good[0], file="absent.md")]))
        refused("is not a path in the tree", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d6.json", [dict(good[0], file="../new.md")]))
        refused("cancel out", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d7.json", [{"file": "docs/x.md", "old": "alpha", "new": "alpha zeta", "shape": "s"},
                                           {"file": "docs/x.md", "old": " zeta", "new": "", "shape": "s"}]))
        refused("is not an ancestor", "make", "--repo", repo, "--base", side, "--key", d, "--out", t / "c1")
        refused("has no commit of its own", "make", "--repo", repo, "--base", tip, "--key", d, "--out", t / "c1")
        refused("is not a commit", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d8.json", good, real_tip="0" * 40))
        refused("a draft holds exactly", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d9.json", good, extra={"copy_commit": tip}))
        refused("is not a key", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d11.json", None, raw="{not json"))
        refused("is not a full commit id", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d12.json", good, real_tip="abc"))
        refused("plants is not a list", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d13.json", {}))
        refused("does not hold exactly", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d14.json", [{"file": "new.md", "old": "5 of 38", "new": "5 of 28"}]))
        refused("a field that is not text", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d15.json", [dict(good[0], new=5)]))
        refused("an empty old text or an empty shape", "make", "--repo", repo, "--base", base, "--out", t / "c1",
                "--key", draft("d16.json", [dict(good[0], shape=" ")]))
        inner = repo / "inner-draft.json"
        inner.write_text(json.dumps({"real_tip": tip, "plants": good}))
        refused("inside the parcel's repository", "make", "--repo", repo, "--base", base, "--key", inner,
                "--out", t / "c1")
        inner.unlink()
        refused("inside the parcel's repository", "make", "--repo", repo, "--base", base, "--key", d,
                "--out", repo / "copy-inside")
        refused("inside the copy", "make", "--repo", repo, "--base", base, "--key", d, "--out", t / "c1",
                "--key-out", t / "c1" / "key.json")
        plain = t / "plain"
        plain.mkdir()
        refused("as a repository: ", "make", "--repo", plain, "--base", base, "--key", d, "--out", t / "c1")
        refused("is not a directory", "make", "--repo", t / "absent", "--base", base, "--key", d, "--out", t / "c1")
        shallow = t / "shallow-clone"
        sh("clone", "-q", "--depth", "1", "file://" + repo.resolve().as_posix(), str(shallow), cwd=t)
        refused("is a shallow repository", "make", "--repo", shallow, "--base", base, "--key", d, "--out", t / "c1")
        wt = t / "worktree"
        sh("worktree", "add", "-q", "-b", "wt", str(wt), tip, cwd=repo)
        refused("inside the parcel's git directory", "make", "--repo", wt, "--base", base, "--key", d,
                "--out", repo / ".git" / "copy-in-git-dir")
        second = t / "second"
        second.mkdir()
        sh("init", "-q", cwd=second)
        (second / "a.md").write_bytes(b"one\n")
        sh("add", "-A", cwd=second)
        sh("commit", "-q", "-m", "base", cwd=second)
        base2 = sh("rev-parse", "HEAD", cwd=second)
        link = sh("hash-object", "-w", "--stdin", cwd=second, data=b"a.md")
        sh("update-index", "--add", "--cacheinfo", "120000,%s,link.md" % link, cwd=second)
        (second / "b.md").write_bytes(b"the same words\n")
        (second / "c.md").write_bytes(b"the same words\n")
        sh("add", "b.md", "c.md", cwd=second)
        sh("commit", "-q", "-m", "a link and two twins", cwd=second)
        tip2 = sh("rev-parse", "HEAD", cwd=second)
        refused("is not a regular file", "make", "--repo", second, "--base", base2, "--out", t / "c1",
                "--key", draft("d17.json", [{"file": "link.md", "old": "a", "new": "b", "shape": "s"}], real_tip=tip2))
        refused("holds the same text as c.md", "make", "--repo", second, "--base", base2, "--out", t / "c1",
                "--key", draft("d18.json", [{"file": "b.md", "old": "same", "new": "very same", "shape": "s"}],
                               real_tip=tip2))
        check(not (t / "c1").exists() or not any((t / "c1").iterdir()), "refused makes leave nothing behind")
        fourth = t / "fourth"
        fourth.mkdir()
        sh("init", "-q", cwd=fourth)
        (fourth / "f.md").write_bytes(b"one\n")
        sh("add", "f.md", cwd=fourth)
        imported = sh("hash-object", "-t", "commit", "-w", "--literally", "--stdin", cwd=fourth, data=(
            "tree %s\nauthor a <a@example.invalid> 1234567890 +99999\ncommitter a <a@example.invalid> 1234567890 "
            "+99999\n\nan imported commit, its time zone out of range\n" % sh("write-tree", cwd=fourth)).encode())
        sh("update-ref", "refs/heads/main", imported, cwd=fourth)
        sh("reset", "-q", "--hard", cwd=fourth)
        (fourth / "f.md").write_bytes(b"the count is 5 of 38\n")
        sh("commit", "-q", "-am", "the parcel's tip", cwd=fourth)
        refused("badTimezone", "make", "--repo", fourth, "--base", imported, "--out", t / "c1", "--key",
                draft("d23.json", [{"file": "f.md", "old": "5 of 38", "new": "5 of 28", "shape": "s"}],
                      real_tip=sh("rev-parse", "HEAD", cwd=fourth)))
        refused("git fsck flags one of their objects, so make cannot build a copy check would pass", "make", "--repo",
                fourth, "--base",
                imported, "--out", t / "c1", "--key", draft("d22.json", [{"file": "f.md", "old": "5 of 38",
                                                                          "new": "5 of 28", "shape": "s"}],
                                                          real_tip=sh("rev-parse", "HEAD", cwd=fourth)))
        check(not (t / "c1").exists() or not any((t / "c1").iterdir()), "refused makes leave nothing behind")
        refused("README.md's text at real_tip is in the base's history", "make", "--repo", repo, "--base", base,
                "--out", t / "c1", "--key",
                draft("d19.json", [{"file": "README.md", "old": "hello", "new": "hullo", "shape": "s"}]))
        third = t / "third"
        third.mkdir()
        sh("init", "-q", cwd=third)
        (third / "f.md").write_bytes(b"the count is 5 of 38\n")
        (third / "g.md").write_bytes(b"words of 38\n")
        sh("add", "-A", cwd=third)
        sh("commit", "-q", "-m", "base", cwd=third)
        base3 = sh("rev-parse", "HEAD", cwd=third)
        (third / "f.md").write_bytes(b"the count changed\n")
        sh("commit", "-q", "-am", "the parcel changes f.md", cwd=third)
        (third / "f.md").write_bytes(b"the count is 5 of 38\n")
        sh("mv", "g.md", "h.md", cwd=third)
        sh("commit", "-q", "-am", "the parcel restores f.md and moves g.md", cwd=third)
        tip3 = sh("rev-parse", "HEAD", cwd=third)
        refused("f.md's text at real_tip is in the base's history", "make", "--repo", third, "--base", base3,
                "--out", t / "c1", "--key", draft("d20.json", [{"file": "f.md", "old": "5 of 38", "new": "5 of 28",
                                                               "shape": "s"}], real_tip=tip3))
        refused("h.md's text at real_tip is in the base's history", "make", "--repo", third, "--base", base3,
                "--out", t / "c1", "--key", draft("d21.json", [{"file": "h.md", "old": "of 38", "new": "of 28",
                                                               "shape": "s"}], real_tip=tip3))
        check(not (t / "c1").exists() or not any((t / "c1").iterdir()), "refused makes leave nothing behind")
        empty = t / "empty-copy"
        rc, so, se = run("make", "--repo", repo, "--base", base, "--key", draft("d10.json", []), "--out", empty)
        check(rc == 0 and "0 plants in 0 files" in so, "a key with no plants: %s" % se.strip())
        rc, _, _ = run()
        check(rc == 2, "no arguments is bad usage, exit 2 (got %d)" % rc)
    finally:
        rmtree(t)
    print("plant.py selftest: %d checks, %d failed" % (checks, failed))
    return 0 if failed == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser(prog="plant.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make")
    m.add_argument("--repo", required=True)
    m.add_argument("--base", required=True)
    m.add_argument("--key", required=True)
    m.add_argument("--out", required=True)
    m.add_argument("--key-out")
    m.add_argument("--message")
    m.set_defaults(func=cmd_make)
    h = sub.add_parser("hash")
    h.add_argument("keys", nargs="+")
    h.set_defaults(func=cmd_hash)
    c = sub.add_parser("check")
    c.add_argument("--key", required=True)
    c.add_argument("--repo", required=True)
    c.add_argument("--copy")
    c.add_argument("--dispatch", action="store_true")
    c.add_argument("--sha256")
    c.set_defaults(func=cmd_check)
    ls = sub.add_parser("list")
    ls.add_argument("keys", nargs="+")
    ls.add_argument("--report")
    ls.set_defaults(func=cmd_list)
    s = sub.add_parser("selftest")
    s.set_defaults(func=selftest)
    a = ap.parse_args(argv)
    try:
        return a.func(a) or 0
    except Refused as e:
        print("plant.py: refused: %s" % e, file=sys.stderr)
        return 1
    except Exception as e:
        print("plant.py: the tool failed: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
