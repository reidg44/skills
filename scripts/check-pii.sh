#!/usr/bin/env bash
# Block identifying info from entering this (potentially public) repo.
#
#   check-pii.sh FILE...            scan file contents        (pre-commit)
#   check-pii.sh --commit-msg FILE  scan a commit message     (commit-msg)
#   check-pii.sh --author           require a noreply author/committer email
#
# Generic patterns live here. Personal strings (real name, username, hostname, email)
# go in .pii-denylist, one fixed string per line; it is gitignored so the list itself never leaks.
# A "!string" line in .pii-denylist allows that string everywhere, like a .gitignore negation:
# it is blanked out before checking, so other identifying info on the same line is still caught.
# Silence a one-off false positive by putting "pii-allow" on that line.
set -uo pipefail

root=$(git rev-parse --show-toplevel)
denylist="$root/.pii-denylist"

generic='/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+|[Cc]:\\+Users\\+[A-Za-z0-9._-]+'
generic+='|(^|[^0-9.])(10\.[0-9]{1,3}|192\.168|172\.(1[6-9]|2[0-9]|3[01]))\.[0-9]{1,3}\.[0-9]{1,3}'
generic+='|[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}'
allow='users\.noreply\.github\.com|noreply@anthropic\.com|@example\.(com|org)|pii-allow'
# Commit author/committer must be GitHub noreply; the content allowlist above is too loose for that.
author_allow='^[A-Za-z0-9._+-]+@users\.noreply\.github\.com$'

deny_patterns() { [[ -f $denylist ]] && grep -vE '^\s*(#|!|$)' "$denylist"; }
allow_patterns() { [[ -f $denylist ]] && sed -n 's/^!//p' "$denylist"; }

masked() { # masked <file>: print "N:line" with every allowed string blanked out (case-insensitive)
  awk -v allow="$(allow_patterns)" '
    BEGIN { n = split(tolower(allow), A, "\n") }
    { s = $0; l = tolower(s)
      for (i = 1; i <= n; i++) {
        if (A[i] == "") continue
        while ((p = index(l, A[i])) > 0) {
          pad = sprintf("%" length(A[i]) "s", "")
          s = substr(s, 1, p - 1) pad substr(s, p + length(A[i]))
          l = substr(l, 1, p - 1) pad substr(l, p + length(A[i]))
        }
      }
      print NR ":" s }' "$1"
}

fail=0
report() { echo "✗ identifying info: $1"; fail=1; }

scan() { # scan <label> <file>
  local tmp lines n
  tmp=$(mktemp); cat "$2" >"$tmp"   # <file> may be a pipe, and it is read more than once
  grep -Iq . "$tmp" || { rm -f "$tmp"; return; }   # skip binary and empty files
  lines=$(
    masked "$tmp" | grep -E "$generic" | grep -vE "$allow"
    deny_patterns >/dev/null && masked "$tmp" | grep -iF -f <(deny_patterns) | grep -v 'pii-allow'
  )
  for n in $(cut -d: -f1 <<<"$lines" | sort -un); do report "$1:$n:$(sed -n "${n}p" "$tmp")"; done
  rm -f "$tmp"
}

case "${1:-}" in
  --author)
    for who in GIT_AUTHOR_IDENT GIT_COMMITTER_IDENT; do
      email=$(git var "$who" | sed 's/.*<\(.*\)>.*/\1/')
      grep -qE "$author_allow" <<<"$email" || report "$who email '$email' is not a users.noreply.github.com address"
    done ;;
  --commit-msg)
    scan "commit message" <(grep -v '^#' "$2") ;;
  *)
    for f in "$@"; do scan "$f" "$f"; done ;;
esac

[[ -f $denylist ]] || echo "⚠ no .pii-denylist, so only generic patterns were checked (see README)" >&2
exit $fail
