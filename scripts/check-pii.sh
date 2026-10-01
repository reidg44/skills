#!/usr/bin/env bash
# Block identifying info from entering this (potentially public) repo.
#
#   check-pii.sh FILE...            scan file contents        (pre-commit)
#   check-pii.sh --commit-msg FILE  scan a commit message     (commit-msg)
#   check-pii.sh --author           require a noreply author/committer email
#
# Generic patterns live here. Personal strings (real name, username, hostname, email)
# go in .pii-denylist, one fixed string per line; it is gitignored so the list itself never leaks.
# Silence a deliberate false positive by putting "pii-allow" on that line.
set -uo pipefail

root=$(git rev-parse --show-toplevel)
denylist="$root/.pii-denylist"

generic='/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+|[Cc]:\\+Users\\+[A-Za-z0-9._-]+'
generic+='|(^|[^0-9.])(10\.[0-9]{1,3}|192\.168|172\.(1[6-9]|2[0-9]|3[01]))\.[0-9]{1,3}\.[0-9]{1,3}'
generic+='|[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}'
allow='users\.noreply\.github\.com|noreply@anthropic\.com|@example\.(com|org)|pii-allow'
# Commit author/committer must be GitHub noreply; the content allowlist above is too loose for that.
author_allow='^[A-Za-z0-9._+-]+@users\.noreply\.github\.com$'

deny_patterns() { [[ -f $denylist ]] && grep -vE '^\s*(#|$)' "$denylist"; }

fail=0
report() { echo "✗ identifying info: $1"; fail=1; }

scan() { # scan <label> <file>
  local hits
  hits=$(grep -nIE "$generic" "$2" | grep -vE "$allow")
  [[ -n $hits ]] && while IFS= read -r l; do report "$1:$l"; done <<<"$hits"
  if deny_patterns >/dev/null; then
    hits=$(grep -nIiF -f <(deny_patterns) "$2" | grep -v 'pii-allow')
    [[ -n $hits ]] && while IFS= read -r l; do report "$1:$l"; done <<<"$hits"
  fi
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
