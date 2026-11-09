#!/usr/bin/env bash
# Run a skill's eval suite with `claude plugin eval`.
#
#   evals/run.sh <skill-name> [extra claude plugin eval options…]
#   evals/run.sh inspect --case python-service-focused --runs 1
#
# Eval cases live in evals/<skill-name>/, outside the skill folder, so people
# who install a skill get only the skill. `claude plugin eval` looks for cases
# in <skill>/evals/, so this links them in for the run and removes the link
# afterwards, even if the run fails or is interrupted.
#
# These are real, billed model runs (with and without the skill), and each
# case's scaffold script copies its fixture repo into the run's workspace.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
name="${1:?usage: evals/run.sh <skill-name> [claude plugin eval options…]}"
shift

skill="$repo/skills/$name"
cases="$repo/evals/$name"
link="$skill/evals"

[ -d "$skill" ] || { echo "no skill at skills/$name" >&2; exit 1; }
[ -d "$cases" ] || { echo "no eval cases at evals/$name" >&2; exit 1; }
[ -e "$link" ] && { echo "skills/$name/evals already exists; remove it first" >&2; exit 1; }

ln -s "../../evals/$name" "$link"
trap 'rm -f "$link"' EXIT

cd "$skill"
claude plugin eval . --scaffold --allow-tools Write,Edit,Bash,Agent --no-publish "$@"
