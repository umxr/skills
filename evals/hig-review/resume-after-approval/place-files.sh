#!/usr/bin/env bash
set -eu
here="$(dirname "$0")"
cp -R "$here/../small-app-review/files/." .
git init -q -b main
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -q -m "Fernleaf 1.4.0"
cp -R "$here/files/." .
