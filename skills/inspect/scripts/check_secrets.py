#!/usr/bin/env python3
"""Check that written files don't leak any part of a secret found in the repo.

Usage:
    python3 check_secrets.py <repo-root> <file> [<file> ...]

Finds secret values in the repo with the same detectors as inventory.py
(committed .env-style files, credentials in URLs, hard-coded secret
assignments, env-var fallbacks, known key formats), then checks each given
file for any fragment of those values: the whole value, or any 8-character
piece of it — counting only fragments that don't also appear elsewhere in the
repo, so a project name, hostname or variable name that merely occurs inside a
value isn't flagged. Local-dev credentials (localhost and compose service
hosts) are not treated as secrets. Prints each hit
as `file:line` plus which secret it came from, without printing the value.
Exit code 1 if anything leaks, 0 if clean. Standard library only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inventory as inv  # noqa: E402

WINDOW = 8
QUOTED = re.compile(r"""(['"])([^'"\s]{8,})\1""")
URL_CRED = re.compile(r"[a-z][a-z0-9+.-]*://[^\s:/@'\"]+:([^\s@'\"]{3,})@", re.I)
ENV_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)\s*$")


def secret_values(root: Path, files: list[str]) -> list[tuple[str, int, str, str]]:
    """(file, line, label, value) for each secret value in the repo."""
    out = []
    for f in files:
        text = inv.read_text(root / f)
        if text is None:
            continue
        is_secret_file = bool(inv.SECRET_FILE_RE.search(f)) and not inv.SECRET_FILE_OK_RE.search(f)
        for i, line in enumerate(text.splitlines(), 1):
            if len(line) > 400:
                continue
            found = []
            for m in URL_CRED.finditer(line):
                if not re.search(r"@(localhost|127\.0\.0\.1|0\.0\.0\.0|db|postgres|mysql|redis)[:/]", line[m.start():]):
                    found.append(("password in URL", m.group(1)))
            if is_secret_file:
                m = ENV_LINE.match(line)
                if m and not URL_CRED.search(m.group(2)):
                    found.append((m.group(1), m.group(2).strip("'\"")))
            for kind, rx in inv.SECRET_PATTERNS:
                if rx.search(line) and kind != "credentials in URL":
                    for q in QUOTED.finditer(line):
                        found.append((kind, q.group(2)))
                    m = rx.search(line)
                    if kind not in ("hard-coded secret assignment", "secret used as env-var fallback default"):
                        found.append((kind, m.group(0)))
            for label, value in found:
                if len(value) >= 6 and not inv.PLACEHOLDER_RE.search(value):
                    out.append((f, i, label, value))
    return out


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    root = Path(sys.argv[1])
    targets = [Path(p) for p in sys.argv[2:]]
    files, _, _ = inv.list_files(root, 150_000)
    target_rel = {str(t.resolve().relative_to(root.resolve())) for t in targets
                  if t.resolve().is_relative_to(root.resolve())}
    # The inspection's own outputs (wherever they are) are never evidence of
    # what's in the codebase.
    files = [f for f in files if f not in target_rel
             and f.rsplit("/", 1)[-1] not in ("CONTEXT.md", "CODEBASE_REPORT.md")]
    secrets = secret_values(root, files)

    # Text of the repo outside each secret's own line, to tell secret-specific
    # fragments from ones that occur anyway (project names, hosts, keys).
    corpus = []
    for f in files:
        t = inv.read_text(root / f)
        if t is not None:
            corpus.append((f, t.splitlines()))

    def elsewhere(fragment: str, src: str, src_line: int) -> bool:
        for f, lines in corpus:
            for i, line in enumerate(lines, 1):
                if fragment in line and not (f == src and i == src_line):
                    return True
        return False

    hits = 0
    for t in targets:
        text = t.read_text(errors="replace") if t.exists() else ""
        for f, i, label, value in secrets:
            frags = {value} | {value[k:k + WINDOW] for k in range(0, max(len(value) - WINDOW + 1, 0))}
            for frag in sorted(frags, key=len, reverse=True):
                if frag in text and not elsewhere(frag, f, i):
                    ln = next(n for n, l in enumerate(text.splitlines(), 1) if frag in l)
                    kind = "the full value" if frag == value else f"a {len(frag)}-char fragment"
                    print(f"LEAK {t}:{ln} — {kind} of {label} from {f}:{i}")
                    hits += 1
                    break
    if not hits:
        print(f"clean: {len(targets)} file(s) checked against {len(secrets)} secret value(s) found in the repo")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
