#!/usr/bin/env bash
# The ledger's two writes, with the stamp taken from the clock, never typed (ParcelRound METHOD.md section 4; the
# ledger's README, method/parcelround/templates/ledger.md: "Write each heading's time from `date`, never from memory").
#
#   tools/ledger.sh append LEDGER AUTHOR "headline" < body
#       Appends an entry to LEDGER/AUTHOR.md. The body comes from stdin and must hold a Measured: line, a Believed:
#       line and a For: line (the ledger's entry format), and no level-1 or level-2 heading of its own, in either
#       of Markdown's spellings: no line that begins, up to three spaces in, with # or ## and then a space, a tab or
#       its end, and no line of - or of = right under a line that holds text. It does not parse Markdown's blocks,
#       so it reads those lines wherever they are, a fenced code block included: indent a code block four spaces
#       instead, and its lines are not read so. A heading that follows > or a list item's marker on its line, or
#       that is written in HTML, is not refused. A level-3 heading may divide the entry.
#       The heading is "## <date> - <headline>", its date from `date`, in the shape the archived ledgers use
#       ("## 2026-10-02 21:37:58 -0700 - ..."). The headline is one line.
#   tools/ledger.sh urgent LEDGER AUTHOR SLUG "headline" < body
#       Writes one urgent message, LEDGER/urgent/AUTHOR-SLUG.md: composed in LEDGER, then renamed into urgent/, so a
#       watcher never sees half of it. Its first line is the headline, which is one line, and the body must hold
#       a For: line. A message that is already there is never replaced.
#   tools/ledger.sh selftest
#       Runs each write, and a case for each refusal, in a temporary directory.
#
# It never edits an entry: a correction is a new entry that names the one it corrects. A "see <time>" line beneath
# the older entry, which the README allows, is written by hand: this tool only appends at the end. Its heading's
# hyphen is the archived ledgers'; the README's template shows a dash. It does not watch: arm the watcher inline,
# from the ledger's README. Exit 0 on success, 1 on a refusal, which names its reason, 2 on bad usage.
set -euo pipefail

die () { echo "ledger.sh: refused: $*" >&2; exit 1; }
usage () { awk 'NR >= 5 && /^set -euo/ { exit } NR >= 5 { sub(/^# ?/, ""); print }' "$0" >&2; exit 2; }
stamp () { date '+%Y-%m-%d %H:%M:%S %z'; }

check_name () {   # <what> <value>: a name that cannot leave the directory it is put in
  case "$2" in
    ""|*/*|*\\*|.*|*..*) die "the $1 '$2' is not a plain name (no slash, no leading dot, no ..)";;
  esac
}

check_headline () {   # <headline>: one line, and not empty
  [ -n "$1" ] || die "an empty headline"
  case "$1" in *$'\n'*|*$'\r'*) die "the headline is more than one line";; esac
}

need_lines () {   # <body> <label>...: each label must start a line of the body
  local body=$1; shift
  local l
  for l in "$@"; do
    grep -q "^$l" <<<"$body" || die "the body has no '$l' line (the ledger's entry format)"
  done
}

append () {
  [ $# -eq 3 ] || usage
  local ledger=$1 author=$2 headline=$3 body
  [ -d "$ledger" ] || die "no ledger directory at $ledger"
  check_name author "$author"
  check_headline "$headline"
  body=$(cat)
  need_lines "$body" "Measured:" "Believed:" "For:"
  # Both of Markdown's spellings of a level-1 or level-2 heading, in one pass, wherever the line is: "atx", a line
  # begun, up to three spaces in, by # or ## and then a space, a tab or its end; "setext", a line of = or of -, up
  # to three spaces in, right under a line that holds text. A CR LF ends one line, as a lone CR or LF does. It does
  # not parse Markdown's blocks, which only a full parser reads right (v1's fourth re-check found a fence tracker
  # that let a heading through), so it errs toward refusing: a fenced block's # lines, and --- under a list item.
  # The body is read from a here-string, never a pipe, and awk reads all of it: a reader that leaves a pipe early,
  # under pipefail, would turn a large body's answer round.
  local kind
  kind=$(awk '
      kind != "" { next }
      { sub(/\r$/, ""); n = split($0, part, "\r"); if (n == 0) { n = 1; part[1] = "" }
        for (i = 1; i <= n && kind == ""; i++) {
          if (part[i] ~ /^ ? ? ?##?([ \t]|$)/) kind = "atx"
          else if (prev ~ /[^ \t]/ && part[i] ~ /^ ? ? ?(=+|-+)[ \t]*$/) kind = "setext"
          prev = part[i] } }
      END { print kind }' <<<"$body")
  [ "$kind" != atx ] || die "the body holds a heading line ('# ...' or '## ...'): a heading is this tool's to" \
    "write, from date. This tool reads such a line in a fenced code block too: indent the block four spaces"
  [ "$kind" != setext ] || die "the body holds a line of '=' or '-' under a text line, which Markdown reads as a" \
    "heading: put a blank line above it, or, in a code block, indent the block four spaces"
  printf '\n## %s - %s\n\n%s\n' "$(stamp)" "$headline" "$body" >> "$ledger/$author.md"
  echo "appended to $ledger/$author.md"
}

urgent () {
  [ $# -eq 4 ] || usage
  local ledger=$1 author=$2 slug=$3 headline=$4 body tmp dest
  [ -d "$ledger" ] || die "no ledger directory at $ledger"
  check_name author "$author"; check_name slug "$slug"
  check_headline "$headline"
  body=$(cat)
  need_lines "$body" "For:"
  mkdir -p "$ledger/urgent"
  dest="$ledger/urgent/$author-$slug.md"
  [ ! -e "$dest" ] || die "$dest is already there, and a message is never replaced: choose another slug"
  tmp=$(mktemp "$ledger/.compose-$author-XXXXXX")
  printf '%s\n%s\n\nWritten: %s\n' "$headline" "$body" "$(stamp)" > "$tmp"
  mv -n "$tmp" "$dest" 2>/dev/null || true
  if [ -e "$tmp" ]; then rm -f "$tmp"; die "$dest appeared while this one was composed; not replaced"; fi
  echo "urgent: $dest"
}

selftest () {
  local self n=0 failed=0
  self=$(cd "$(dirname "$0")" && pwd)/$(basename "$0")
  T=$(mktemp -d)
  trap "rm -rf '$T'" EXIT
  ok () {   # <command>: must succeed
    n=$((n+1))
    "$@" >/dev/null 2>&1 || { failed=$((failed+1)); echo "FAIL: $*"; }
  }
  refused () {   # <reason> <command>: must exit 1 and name the reason
    local want=$1 err rc=0; shift; n=$((n+1))
    err=$("$@" 2>&1 >/dev/null) || rc=$?
    if [ "$rc" -ne 1 ] || ! printf '%s' "$err" | grep -q "^ledger.sh: refused: .*$want"; then
      failed=$((failed+1)); echo "FAIL: want exit 1 naming '$want', got exit $rc ($err): $*"
    fi
  }
  local L="$T/L" body="Measured: x
Believed: y
For: anyone"
  mkdir "$L"
  ok bash -c "printf '%s\n' '$body' | '$self' append '$L' P1 'first'"
  ok bash -c "printf '%s\n' '$body' | '$self' append '$L' P1 'second'"
  ok bash -c "[ \$(grep -c '^## ' '$L/P1.md') -eq 2 ]"
  ok bash -c "grep -Eq '^## [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [+-][0-9]{4} - first\$' '$L/P1.md'"
  refused "no 'For:' line" bash -c "printf 'Measured: x\nBelieved: y\n' | '$self' append '$L' P1 'no For line'"
  refused "no 'Measured:' line" bash -c "printf 'Believed: y\nFor: z\n' | '$self' append '$L' P1 'no Measured line'"
  refused "not a plain name" bash -c "printf '%s\n' '$body' | '$self' append '$L' ../P1 'a path for a name'"
  refused "not a plain name" bash -c "printf '%s\n' '$body' | '$self' append '$L' .P1 'a hidden name'"
  refused "no ledger directory" bash -c "printf '%s\n' '$body' | '$self' append '$T/none' P1 'no ledger'"
  refused "an empty headline" bash -c "printf '%s\n' '$body' | '$self' append '$L' P1 ''"
  ok bash -c "[ \$(grep -c '^## ' '$L/P1.md') -eq 2 ]"
  ok bash -c "printf 'For: P2\n' | '$self' urgent '$L' lead brief-fix 'P2: your brief is wrong about X'"
  ok bash -c "[ \"\$(head -1 '$L/urgent/lead-brief-fix.md')\" = 'P2: your brief is wrong about X' ]"
  ok bash -c "grep -q '^For: P2' '$L/urgent/lead-brief-fix.md'"
  refused "never replaced" bash -c "printf 'For: P2\n' | '$self' urgent '$L' lead brief-fix 'the same name again'"
  ok bash -c "[ \"\$(head -1 '$L/urgent/lead-brief-fix.md')\" = 'P2: your brief is wrong about X' ]"
  refused "no 'For:' line" bash -c "printf 'no For line\n' | '$self' urgent '$L' lead other 'x'"
  refused "not a plain name" bash -c "printf 'For: P2\n' | '$self' urgent '$L' lead ../escape 'x'"
  ok bash -c "! ls -a '$L' | grep -q '^\.compose-'"
  ok bash -c "[ \$(ls '$L/urgent' | wc -l) -eq 1 ]"
  printf 'Measured: x\nFor: z\n' > "$T/no-believed"
  refused "no 'Believed:' line" bash -c '"$0" append "$1" P1 "no Believed line" < "$2"' "$self" "$L" "$T/no-believed"
  printf '%s\n## 2026-01-01 00:00:00 +0000 - a typed heading\n' "$body" > "$T/typed"
  refused "holds a heading line" bash -c '"$0" append "$1" P1 "a typed heading" < "$2"' "$self" "$L" "$T/typed"
  printf '%s\n   ## indented\n' "$body" > "$T/typed2"
  refused "holds a heading line" bash -c '"$0" append "$1" P1 "an indented heading" < "$2"' "$self" "$L" "$T/typed2"
  printf '%s\n##\ttabbed\n' "$body" > "$T/typed3"
  refused "holds a heading line" bash -c '"$0" append "$1" P1 "a tabbed heading" < "$2"' "$self" "$L" "$T/typed3"
  printf '%s\rx\r## after a carriage return\n' "$body" > "$T/typed4"
  refused "holds a heading line" bash -c '"$0" append "$1" P1 "a CR heading" < "$2"' "$self" "$L" "$T/typed4"
  printf '%s\n# a level-1 heading\n' "$body" > "$T/typed5"
  refused "holds a heading line" bash -c '"$0" append "$1" P1 "a level-1 heading" < "$2"' "$self" "$L" "$T/typed5"
  printf '%s\nan underlined line\n---\n' "$body" > "$T/setext"
  refused "under a text line" bash -c '"$0" append "$1" P1 "a setext heading" < "$2"' "$self" "$L" "$T/setext"
  printf 'Measured: x\r\nBelieved: y\r\nFor: z\r\nunderlined\r\n  ===  \r\n' > "$T/setext2"
  refused "under a text line" bash -c '"$0" append "$1" P1 "a CR LF setext heading" < "$2"' \
    "$self" "$L" "$T/setext2"
  printf '%s\runderlined\r-\n' "$body" > "$T/setext3"
  refused "under a text line" bash -c '"$0" append "$1" P1 "a CR setext heading" < "$2"' "$self" "$L" "$T/setext3"
  printf '%s\n### a sub-heading is allowed\n' "$body" > "$T/sub"
  ok bash -c '"$0" append "$1" P3 "a sub-heading" < "$2"' "$self" "$L" "$T/sub"
  printf '%s\n\n---\nnot underlined\n    ---\n' "$body" > "$T/rule"
  ok bash -c '"$0" append "$1" P3 "a rule under a blank line, and dashes four spaces in" < "$2"' \
    "$self" "$L" "$T/rule"
  printf '%s\n```sh\n# run the gate\nbash verify/run.sh\n```\n' "$body" > "$T/fenced"
  refused "in a fenced code block too" bash -c '"$0" append "$1" P1 "a fenced block with a comment" < "$2"' \
    "$self" "$L" "$T/fenced"
  printf '%s\n\n    # run the gate\n    bash verify/run.sh\n    ---\n' "$body" > "$T/indented"
  ok bash -c '"$0" append "$1" P3 "a code block indented four spaces" < "$2"' "$self" "$L" "$T/indented"
  printf '%s\n\n<!--\n```\n-->\n## 2026-10-23 12:00:00 +0000 - forged\n' "$body" > "$T/html"
  refused "holds a heading line" bash -c '"$0" append "$1" P1 "a fence marker in an HTML block" < "$2"' \
    "$self" "$L" "$T/html"
  printf '%s\n\n- item\n  ```\n## 2026-10-23 12:00:00 +0000 - forged\n' "$body" > "$T/item"
  refused "holds a heading line" bash -c '"$0" append "$1" P1 "an unclosed fence in a list item" < "$2"' \
    "$self" "$L" "$T/item"
  printf '%s\n```\n# never closed\n' "$body" > "$T/open"
  refused "holds a heading line" bash -c '"$0" append "$1" P1 "a fence never closed" < "$2"' \
    "$self" "$L" "$T/open"
  awk 'BEGIN { for (i = 0; i < 4000; i++) print "filler line " i " of a body larger than a pipe holds" }' > "$T/filler"
  { printf '%s\n' "$body"; cat "$T/filler"; } > "$T/big"
  ok bash -c '"$0" append "$1" P4 "a large body" < "$2"' "$self" "$L" "$T/big"
  { printf '%s\n## 2026-01-01 00:00:00 +0000 - typed\n' "$body"; cat "$T/filler"; } > "$T/big-atx"
  refused "holds a heading line" bash -c '"$0" append "$1" P1 "a large body, a heading" < "$2"' "$self" "$L" "$T/big-atx"
  { printf '%s\nunderlined\n---\n' "$body"; cat "$T/filler"; } > "$T/big-setext"
  refused "under a text line" bash -c '"$0" append "$1" P1 "a large body, a setext heading" < "$2"' \
    "$self" "$L" "$T/big-setext"
  printf '%s\n' "$body" > "$T/body-cr"
  refused "more than one line" bash -c '"$0" append "$1" P1 "$2" < "$3"' "$self" "$L" "$(printf 'one\rtwo')" "$T/body-cr"
  printf '%s\n' "$body" > "$T/body"
  refused "more than one line" bash -c '"$0" append "$1" P1 "$2" < "$3"' "$self" "$L" "$(printf 'two\nlines')" "$T/body"
  refused "more than one line" bash -c 'printf "For: P2\n" | "$0" urgent "$1" lead two "$2"' "$self" "$L" "$(printf 'two\nlines')"
  refused "an empty headline" bash -c 'printf "For: P2\n" | "$0" urgent "$1" lead empty ""' "$self" "$L"
  refused "no ledger directory" bash -c 'printf "For: P2\n" | "$0" urgent "$1/none" lead x "h"' "$self" "$T"
  local before after got
  before=$(date '+%Y-%m-%d %H:%M')
  "$self" append "$L" P2 'fresh' < "$T/body" >/dev/null
  after=$(date '+%Y-%m-%d %H:%M')
  got=$(sed -n 's/^## \([0-9-]* [0-9]*:[0-9]*\):[0-9]* [+-][0-9]* - fresh$/\1/p' "$L/P2.md")
  n=$((n+1))
  [ "$got" = "$before" ] || [ "$got" = "$after" ] || {
    failed=$((failed+1)); echo "FAIL: the heading's stamp '$got' is not the clock's, $before"; }
  mkdir "$T/bin"
  printf '#!/bin/sh\n: > "$3"\nexec "$REAL_MV" "$@"\n' > "$T/bin/mv"
  chmod +x "$T/bin/mv"
  refused "appeared while this one was composed" env PATH="$T/bin:$PATH" REAL_MV="$(command -v mv)" \
    bash -c 'printf "For: P2\n" | "$0" urgent "$1" lead race "a message that loses the race"' "$self" "$L"
  ok bash -c "[ ! -s '$L/urgent/lead-race.md' ]"
  ok bash -c "! ls -a '$L' | grep -q '^\.compose-'"
  local rc=0; "$self" >/dev/null 2>&1 || rc=$?
  n=$((n+1)); [ "$rc" -eq 2 ] || { failed=$((failed+1)); echo "FAIL: no arguments should exit 2, got $rc"; }
  echo "ledger.sh selftest: $n checks, $failed failed"
  [ "$failed" -eq 0 ]
}

[ $# -ge 1 ] || usage
cmd=$1; shift
case "$cmd" in
  append) append "$@";;
  urgent) urgent "$@";;
  selftest) [ $# -eq 0 ] || usage; selftest;;
  *) usage;;
esac
