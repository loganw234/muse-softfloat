#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""fetch.py - pinned workload download for the demo (helper of fetch.sh).

Reads the REBOUND and KissFFT rows (by name, nothing else) from
docs/metrics/fetches.jsonl, downloads those two archives into the
demo cache, verifies the archive sha256 and then the licence
sha256 (licence bytes read from inside the archive) against the
fetches rows, and only then extracts.  With --offline no network
is touched: the archives must already be in the cache with the
recorded hashes, or the run fails naming the missing file.

Layout produced (all under the gitignored cache dir):
  archives/<archive-file>   verified downloads, kept for --offline
  src/rebound/              extracted REBOUND tree (src/ inside)
  src/kissfft/              extracted KissFFT tree
  src/<key>.fetch-ok        marker naming the archive sha256 used

Exit status: 0 = both workloads fetched and verified; 1 = a hash
or archive-shape failure; 2 = usage / prerequisite failure.
"""
import hashlib
import json
import pathlib
import shutil
import sys
import tarfile
import urllib.request

# name in fetches.jsonl -> (cache key, licence path below the
# archive's single root directory).  The licence paths are the
# files whose sha256 the fetches rows record (REBOUND root
# LICENSE; KissFFT LICENSES/BSD-3-Clause).
PACKAGES = [
    ("REBOUND", "rebound", "LICENSE"),
    ("KissFFT", "kissfft", "LICENSES/BSD-3-Clause"),
]


def fail(msg, code=1):
    print("fetch: FAIL - %s" % msg)
    return code


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_hex64(s):
    return (isinstance(s, str) and len(s) == 64
            and all(c in "0123456789abcdef" for c in s))


def load_rows(fetches_path):
    rows = {}
    with open(fetches_path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                raise SystemExit(
                    fail("%s line %d is not JSON" % (fetches_path, ln), 2))
            name = row.get("name")
            if name in dict((p[0], p) for p in PACKAGES):
                if name in rows:
                    raise SystemExit(
                        fail("duplicate %s row in %s" % (name, fetches_path), 2))
                rows[name] = row
    return rows


def download(url, dest_partial):
    req = urllib.request.Request(url, headers={"User-Agent": "muse-softfloat-demo-fetch"})
    total = 0
    with urllib.request.urlopen(req) as resp, open(dest_partial, "wb") as out:
        for chunk in iter(lambda: resp.read(1024 * 256), b""):
            out.write(chunk)
            total += len(chunk)
    return total


def archive_root_and_licence(archive, licence_rel):
    """Return (root_name, licence_bytes) from the tar member list,
    without extracting anything."""
    with tarfile.open(archive, "r:gz") as tf:
        roots = set()
        licence_member = None
        for m in tf.getmembers():
            parts = [p for p in m.name.split("/") if p not in ("", ".")]
            if not parts:
                continue
            roots.add(parts[0])
            if "/".join(parts[1:]) == licence_rel and m.isfile():
                if licence_member is not None:
                    raise ValueError("more than one %s in archive" % licence_rel)
                licence_member = m
        if len(roots) != 1:
            raise ValueError("expected one archive root, found %s"
                             % sorted(roots))
        if licence_member is None:
            raise ValueError("licence file %s not found in archive"
                             % licence_rel)
        data = tf.extractfile(licence_member).read()
    return roots.pop(), data


def extract_tree(archive, dest_dir, root_name):
    """Extract archive into dest_dir via a temp sibling, then move
    the archive root to dest_dir itself."""
    tmp_dir = dest_dir.with_name(dest_dir.name + ".extract-tmp")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)
    with tarfile.open(archive, "r:gz") as tf:
        try:
            tf.extractall(tmp_dir, filter="data")
        except TypeError:  # older Python without extraction filters
            tf.extractall(tmp_dir)
    extracted_root = tmp_dir / root_name
    if not extracted_root.is_dir():
        raise ValueError("archive root %s missing after extraction"
                         % root_name)
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    shutil.move(str(extracted_root), str(dest_dir))
    shutil.rmtree(tmp_dir)


def fetch_one(name, key, licence_rel, row, cache, offline):
    for field in ("url", "archive_sha256", "licence_sha256", "version"):
        if field not in row:
            return fail("%s fetches row lacks %r" % (name, field), 2)
    if not is_hex64(row["archive_sha256"]) or not is_hex64(row["licence_sha256"]):
        return fail("%s fetches row has a malformed sha256" % name, 2)
    url = row["url"]
    # The pinned URLs end in a bare commit/tag (".../262a9cce....tar.gz",
    # ".../131.2.0.tar.gz"); prefix the package key so cached archives
    # say what they are (rebound-<commit>.tar.gz, kissfft-131.2.0.tar.gz).
    archive_name = "%s-%s" % (key, url.rstrip("/").rsplit("/", 1)[-1])
    if not archive_name.endswith((".tar.gz", ".tgz")):
        return fail("%s url does not name a .tar.gz archive: %s" % (name, url), 2)
    archives_dir = cache / "archives"
    src_dir = cache / "src"
    archives_dir.mkdir(parents=True, exist_ok=True)
    src_dir.mkdir(parents=True, exist_ok=True)
    archive = archives_dir / archive_name
    tree_dir = src_dir / key
    marker = src_dir / (key + ".fetch-ok")
    want_archive_sha = row["archive_sha256"]

    net = "cached"
    if archive.is_file() and sha256_file(archive) == want_archive_sha:
        pass
    elif offline:
        where = "missing" if not archive.is_file() else "hash mismatch"
        return fail("--offline: %s archive %s at %s (seed the cache by "
                    "running demo/fetch.sh once with network, or copy the "
                    "pinned archive there by hand)" % (name, where, archive))
    else:
        partial = archives_dir / (".partial-" + archive_name)
        print("fetch: downloading %s (%s)" % (name, url))
        try:
            n = download(url, partial)
        except Exception as exc:
            partial.unlink(missing_ok=True)
            return fail("download of %s failed: %s" % (url, exc))
        got = sha256_file(partial)
        if got != want_archive_sha:
            partial.unlink(missing_ok=True)
            return fail("%s archive sha256 mismatch: got %s, fetches row "
                        "says %s - refusing the download"
                        % (name, got, want_archive_sha))
        partial.replace(archive)
        net = "downloaded %d bytes" % n

    try:
        root_name, licence_bytes = archive_root_and_licence(archive, licence_rel)
    except Exception as exc:
        return fail("%s archive inspection failed: %s" % (name, exc))
    licence_sha = hashlib.sha256(licence_bytes).hexdigest()
    if licence_sha != row["licence_sha256"]:
        return fail("%s licence (%s) sha256 mismatch: got %s, fetches row "
                    "says %s - refusing to extract"
                    % (name, licence_rel, licence_sha, row["licence_sha256"]))

    if (tree_dir.is_dir() and marker.is_file()
            and marker.read_text(encoding="utf-8").strip() == want_archive_sha):
        state = "already extracted"
    else:
        try:
            extract_tree(archive, tree_dir, root_name)
        except Exception as exc:
            return fail("%s extraction failed: %s" % (name, exc))
        marker.write_text(want_archive_sha + "\n", encoding="utf-8", newline="\n")
        state = "extracted"
    print("FETCH %s %s archive-sha256 OK licence-sha256 OK (%s; %s)"
          % (name, row["version"], net, state))
    return 0


def main(argv):
    offline = False
    cache = fetches = None
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == "--offline":
            offline = True
        elif arg == "--cache" and i + 1 < len(argv):
            cache = pathlib.Path(argv[i + 1])
            i += 1
        elif arg == "--fetches" and i + 1 < len(argv):
            fetches = pathlib.Path(argv[i + 1])
            i += 1
        else:
            print("usage: fetch.py --cache DIR --fetches FILE [--offline]")
            return 2
        i += 1
    if cache is None or fetches is None:
        print("usage: fetch.py --cache DIR --fetches FILE [--offline]")
        return 2
    if not fetches.is_file():
        return fail("fetches file not found: %s" % fetches, 2)
    rows = load_rows(fetches)
    for name, key, licence_rel in PACKAGES:
        if name not in rows:
            return fail("no %s row in %s" % (name, fetches), 2)
        rc = fetch_one(name, key, licence_rel, rows[name], cache, offline)
        if rc != 0:
            return rc
    print("fetch: OK (%s)" % ("offline, cache only" if offline else "network allowed"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
