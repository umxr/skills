#!/usr/bin/env python3
"""Deterministic inventory of a codebase, for the inspect skill.

Usage:
    python3 inventory.py <repo-root> [--json <path>] [--max-files N]

Prints a Markdown summary to stdout. With --json, also writes the full
inventory (every package, dependency edge and signal) as JSON.

Standard library only (Python 3.8+; TOML parsing needs 3.11+, and falls back
to a small regex parser before that). It never runs package managers, builds
or network calls: it only reads files and, when the root is a git repo, runs
read-only git commands.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

try:  # Python 3.11+
    import tomllib  # type: ignore
except Exception:  # pragma: no cover
    tomllib = None

# --------------------------------------------------------------------------
# Constants

IGNORED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "bower_components", ".pnpm-store",
    "dist", "build", "out", "target", ".next", ".nuxt", ".svelte-kit", ".turbo",
    ".nx", ".cache", ".parcel-cache", ".vercel", ".output", "coverage",
    ".venv", "venv", "env", "__pycache__", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", ".tox", ".eggs", ".gradle", ".idea", ".vscode", "Pods",
    "DerivedData", ".dart_tool", ".terraform", "vendor", "bazel-bin",
    "bazel-out", "bazel-testlogs",
}

LANG_BY_EXT = {
    ".py": "Python", ".pyi": "Python", ".ipynb": "Jupyter",
    ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".mts": "TypeScript", ".cts": "TypeScript", ".tsx": "TypeScript",
    ".vue": "Vue", ".svelte": "Svelte", ".astro": "Astro",
    ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".kts": "Kotlin",
    ".scala": "Scala", ".groovy": "Groovy", ".clj": "Clojure",
    ".c": "C", ".h": "C/C++ header", ".cc": "C++", ".cpp": "C++", ".cxx": "C++", ".hpp": "C++",
    ".cs": "C#", ".fs": "F#", ".vb": "Visual Basic",
    ".swift": "Swift", ".m": "Objective-C", ".mm": "Objective-C",
    ".rb": "Ruby", ".php": "PHP", ".pl": "Perl", ".lua": "Lua", ".r": "R", ".R": "R",
    ".dart": "Dart", ".ex": "Elixir", ".exs": "Elixir", ".erl": "Erlang",
    ".hs": "Haskell", ".ml": "OCaml", ".zig": "Zig", ".nim": "Nim", ".jl": "Julia",
    ".sol": "Solidity", ".proto": "Protobuf", ".graphql": "GraphQL", ".gql": "GraphQL",
    ".sql": "SQL", ".prisma": "Prisma",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell", ".ps1": "PowerShell",
    ".tf": "Terraform", ".hcl": "HCL", ".nix": "Nix",
    ".html": "HTML", ".css": "CSS", ".scss": "SCSS", ".sass": "SCSS", ".less": "Less",
    ".md": "Markdown", ".mdx": "Markdown", ".rst": "reStructuredText",
    ".yml": "YAML", ".yaml": "YAML", ".json": "JSON", ".toml": "TOML", ".xml": "XML",
}

# Languages that are configuration or prose rather than code.
NON_CODE_LANGS = {"Markdown", "reStructuredText", "YAML", "JSON", "TOML", "XML"}

LOCKFILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock",
    "Cargo.lock", "go.sum", "poetry.lock", "uv.lock", "Pipfile.lock",
    "Gemfile.lock", "composer.lock", "mix.lock", "pubspec.lock", "Podfile.lock",
    "gradle.lockfile", "flake.lock", "packages.lock.json",
}

# file name (or glob) -> what it tells you
MARKERS = {
    "package.json": "Node package", "pnpm-workspace.yaml": "pnpm workspace",
    "lerna.json": "Lerna", "nx.json": "Nx", "turbo.json": "Turborepo",
    "rush.json": "Rush", "deno.json": "Deno", "deno.jsonc": "Deno",
    "Cargo.toml": "Cargo", "go.mod": "Go module", "go.work": "Go workspace",
    "pyproject.toml": "Python project", "setup.py": "Python setup.py",
    "setup.cfg": "Python setup.cfg", "Pipfile": "Pipenv",
    "requirements.txt": "pip requirements", "Gemfile": "Bundler",
    "pom.xml": "Maven", "build.gradle": "Gradle", "build.gradle.kts": "Gradle",
    "settings.gradle": "Gradle settings", "settings.gradle.kts": "Gradle settings",
    "composer.json": "Composer", "mix.exs": "Mix", "Package.swift": "SwiftPM",
    "pubspec.yaml": "Dart/Flutter", "CMakeLists.txt": "CMake", "meson.build": "Meson",
    "WORKSPACE": "Bazel", "WORKSPACE.bazel": "Bazel", "MODULE.bazel": "Bazel",
    "BUCK": "Buck", "pants.toml": "Pants", "flake.nix": "Nix flake",
    "Makefile": "Make", "justfile": "just", "Justfile": "just", "Taskfile.yml": "Task",
    "Dockerfile": "Docker", "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose", "compose.yml": "Docker Compose",
    "compose.yaml": "Docker Compose", "Procfile": "Procfile", "Chart.yaml": "Helm chart",
    "serverless.yml": "Serverless", "vercel.json": "Vercel", "netlify.toml": "Netlify",
    "fly.toml": "Fly.io", "app.json": "App config", "wrangler.toml": "Cloudflare Workers",
    "wrangler.jsonc": "Cloudflare Workers",
    ".gitlab-ci.yml": "GitLab CI", "Jenkinsfile": "Jenkins",
    "azure-pipelines.yml": "Azure Pipelines", ".pre-commit-config.yaml": "pre-commit",
    "tsconfig.json": "TypeScript config", ".eslintrc": "ESLint", ".eslintrc.js": "ESLint",
    ".eslintrc.json": "ESLint", ".eslintrc.cjs": "ESLint", "eslint.config.js": "ESLint",
    "eslint.config.mjs": "ESLint", "biome.json": "Biome", ".prettierrc": "Prettier",
    "ruff.toml": "Ruff", ".ruff.toml": "Ruff", "mypy.ini": "mypy", "tox.ini": "tox",
    "pytest.ini": "pytest", "jest.config.js": "Jest", "jest.config.ts": "Jest",
    "vitest.config.ts": "Vitest", "vitest.config.js": "Vitest",
    "playwright.config.ts": "Playwright", "cypress.config.ts": "Cypress",
    "CODEOWNERS": "CODEOWNERS", ".editorconfig": "EditorConfig",
    ".nvmrc": "Node version pin", ".node-version": "Node version pin",
    ".python-version": "Python version pin", ".tool-versions": "asdf/mise versions",
    "rust-toolchain.toml": "Rust toolchain pin", "rust-toolchain": "Rust toolchain pin",
}
CI_GLOBS = [".github/workflows/*.yml", ".github/workflows/*.yaml",
            ".circleci/config.yml", ".buildkite/*.yml", "bitbucket-pipelines.yml",
            ".drone.yml", ".travis.yml"]

TEST_PATTERNS = [
    re.compile(r"(^|/)(tests?|__tests__|spec|specs|test_?utils?|e2e|integration)(/|$)", re.I),
    re.compile(r"(^|/)test_[^/]+\.py$"), re.compile(r"_test\.(py|go)$"),
    re.compile(r"\.(test|spec)\.[cm]?[jt]sx?$"), re.compile(r"Tests?\.(java|kt|cs|swift)$"),
    re.compile(r"_spec\.rb$"), re.compile(r"_test\.exs$"),
]

TODO_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")

SECRET_PATTERNS = [
    ("AWS access key id", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("private key block", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("Stripe/OpenAI-style secret key", re.compile(r"\bsk_(live|test)_[A-Za-z0-9]{10,}|\bsk-[A-Za-z0-9_-]{20,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("credentials in URL", re.compile(r"[a-z][a-z0-9+.-]*://[^\s:/@'\"]+:[^\s@'\"]{3,}@[^\s'\"]+", re.I)),
    ("hard-coded secret assignment", re.compile(
        r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret)\b"
        r"\s*[:=]\s*['\"][^'\"\s$<{]{6,}['\"]")),
    ("secret used as env-var fallback default", re.compile(
        r"(?i)(?:(?:getenv|environ\.get|env\.get)\s*\(\s*['\"]\w*(?:SECRET|PASSWORD|PASSWD|TOKEN|API_?KEY|PRIVATE_KEY)\w*['\"]\s*,"
        r"|process\.env\.\w*(?:SECRET|PASSWORD|TOKEN|API_?KEY)\w*\s*(?:\?\?|\|\|))\s*['\"][^'\"\s$<{]{8,}['\"]")),
]
SECRET_FILE_RE = re.compile(r"(^|/)(\.env(\.[^/]*)?|id_rsa|id_ed25519|.*\.pem|.*\.p12|.*\.pfx|.*\.key|credentials\.json|service-account.*\.json)$")
SECRET_FILE_OK_RE = re.compile(r"\.(example|sample|template|dist|defaults?)$|\.env\.(example|sample|template|test)$", re.I)
PLACEHOLDER_RE = re.compile(r"(?i)(example|changeme|change_me|placeholder|dummy|xxx+|your[_-]|<|\$\{|localhost:|user:pass|username:password)")

MAX_TEXT_BYTES = 2_000_000

# Packages under these path segments are test fixtures, not part of the product.
FIXTURE_RE = re.compile(r"(^|/)(__fixtures__|fixtures?|test-fixtures|testdata|__tests__|__mocks__|snapshots?)(/|$)", re.I)
EXAMPLE_RE = re.compile(r"(^|/)(examples?|samples?|demos?|templates?|starters?)(/|$)", re.I)


# --------------------------------------------------------------------------
# Helpers

def run_git(root: Path, *args: str, timeout: int = 60) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                             text=True, timeout=timeout)
    except Exception:
        return None
    return out.stdout if out.returncode == 0 else None


def list_files(root: Path, max_files: int) -> tuple[list[str], bool, str]:
    """Return repo-relative POSIX paths, whether truncated, and the method."""
    if run_git(root, "rev-parse", "--is-inside-work-tree"):
        out = run_git(root, "ls-files", "-co", "--exclude-standard", "-z")
        if out is not None:
            files = [f for f in out.split("\0") if f]
            # git ls-files lists submodule roots as entries; keep files only.
            files = [f for f in files if not any(p in IGNORED_DIRS for p in f.split("/")[:-1])]
            files = [f for f in files if (root / f).is_file()]
            files.sort()
            return files[:max_files], len(files) > max_files, "git ls-files"
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS and not d.endswith(".egg-info"))
        rel = Path(dirpath).relative_to(root)
        for fn in sorted(filenames):
            files.append(str(PurePosixPath(*rel.parts, fn)) if rel.parts else fn)
            if len(files) > max_files:
                return files[:max_files], True, "filesystem walk"
    return files, False, "filesystem walk"


def read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return None
        data = path.read_bytes()
    except Exception:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


def load_json(path: Path):
    text = read_text(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except Exception:
        # tolerate // comments and trailing commas (tsconfig / rush style)
        stripped = re.sub(r"(?m)^\s*//.*$", "", text)
        stripped = re.sub(r",(\s*[}\]])", r"\1", stripped)
        try:
            return json.loads(stripped)
        except Exception:
            return None


def load_toml(path: Path):
    text = read_text(path)
    if text is None:
        return None
    if tomllib is not None:
        try:
            return tomllib.loads(text)
        except Exception:
            return None
    return None


def yaml_list(text: str, key: str) -> list[str]:
    """Very small YAML reader: the string items of a top-level list `key:`."""
    items, inside = [], False
    for line in text.splitlines():
        if re.match(rf"^{re.escape(key)}\s*:\s*$", line):
            inside = True
            continue
        if inside:
            m = re.match(r"^\s+-\s*['\"]?([^'\"#]+?)['\"]?\s*(#.*)?$", line)
            if m:
                items.append(m.group(1).strip())
            elif line.strip() and not line.startswith((" ", "\t", "#")):
                break
    return items


def glob_to_regex(pat: str) -> re.Pattern:
    """Path-segment-aware glob: `*` stays inside one segment, `**` spans any."""
    out, i = "", 0
    while i < len(pat):
        if pat.startswith("**/", i):
            out += r"(?:.*/)?"
            i += 3
        elif pat.startswith("**", i):
            out += r".*"
            i += 2
        elif pat[i] == "*":
            out += r"[^/]*"
            i += 1
        elif pat[i] == "?":
            out += r"[^/]"
            i += 1
        else:
            out += re.escape(pat[i])
            i += 1
    return re.compile(rf"^{out}$")


def glob_dirs(root: Path, patterns: list[str], all_dirs: set[str]) -> tuple[list[str], list[str]]:
    """Resolve workspace glob patterns against known directories.

    Returns (matched dirs, patterns that matched nothing)."""
    include, exclude, unmatched = [], [], []
    for p in patterns:
        p = p.strip().rstrip("/")
        neg = p.startswith("!")
        p = p.lstrip("!")
        if p.startswith("./"):
            p = p[2:]
        (exclude if neg else include).append(p)
    matched: set[str] = set()
    for pat in include:
        if pat in ("", "."):
            hits = {""}
        else:
            rx = glob_to_regex(pat)
            hits = {d for d in all_dirs if rx.match(d)}
        if not hits:
            unmatched.append(pat)
        matched |= hits
    ex = [glob_to_regex(e) for e in exclude]
    matched = {d for d in matched if not any(r.match(d) for r in ex)}
    return sorted(matched), unmatched


def lang_of(path: str) -> str | None:
    ext = os.path.splitext(path)[1]
    return LANG_BY_EXT.get(ext) or LANG_BY_EXT.get(ext.lower())


def is_test_path(path: str) -> bool:
    return any(p.search(path) for p in TEST_PATTERNS)


def _links_locally(spec: str, local_version: str | None) -> bool:
    """Would a JS dependency spec resolve to the workspace package of that name?"""
    spec = (spec or "").strip()
    if spec.startswith(("workspace:", "file:", "link:", "portal:")) or spec in ("*", "", "latest"):
        return True
    if not local_version:
        return False
    want = re.findall(r"\d+", spec)
    have = re.findall(r"\d+", local_version)
    return bool(want and have and want[0] == have[0])


def norm_py(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def under(path: str, pkg_dir: str) -> bool:
    return pkg_dir == "" or path == pkg_dir or path.startswith(pkg_dir + "/")


# --------------------------------------------------------------------------
# Package readers. Each returns a dict or None.

def read_node(root: Path, d: str) -> dict | None:
    pj = load_json(root / d / "package.json")
    if not isinstance(pj, dict):
        return None
    deps = {}
    for field in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        for k, v in (pj.get(field) or {}).items():
            deps.setdefault(k, {"spec": str(v), "kind": field})
    entry = {}
    for k in ("main", "module", "types", "bin", "exports"):
        if k in pj:
            entry[k] = pj[k] if not isinstance(pj[k], (dict, list)) else "(see package.json)"
    return {
        "ecosystem": "node", "name": pj.get("name") or d or "(root)",
        "version": pj.get("version"), "private": bool(pj.get("private")),
        "description": pj.get("description"),
        "scripts": pj.get("scripts") or {}, "deps": deps, "entry": entry,
        "manifest": str(PurePosixPath(d, "package.json")) if d else "package.json",
    }


def read_cargo(root: Path, d: str) -> dict | None:
    t = load_toml(root / d / "Cargo.toml")
    if not isinstance(t, dict) or "package" not in t:
        return None
    pkg = t["package"]
    deps = {}
    for field in ("dependencies", "dev-dependencies", "build-dependencies"):
        for k, v in (t.get(field) or {}).items():
            spec = v if isinstance(v, str) else (
                "workspace" if isinstance(v, dict) and v.get("workspace") else
                f"path:{v.get('path')}" if isinstance(v, dict) and v.get("path") else
                str(v.get("version")) if isinstance(v, dict) else str(v))
            deps.setdefault(k, {"spec": spec, "kind": field})
    entry = {}
    if (root / d / "src/main.rs").exists():
        entry["bin"] = str(PurePosixPath(d, "src/main.rs"))
    if (root / d / "src/lib.rs").exists():
        entry["lib"] = str(PurePosixPath(d, "src/lib.rs"))
    ver = pkg.get("version")
    return {
        "ecosystem": "cargo", "name": pkg.get("name", d), "version": ver if isinstance(ver, str) else "workspace",
        "private": pkg.get("publish") is False, "description": pkg.get("description"),
        "scripts": {}, "deps": deps, "entry": entry,
        "manifest": str(PurePosixPath(d, "Cargo.toml")) if d else "Cargo.toml",
    }


def read_go(root: Path, d: str) -> dict | None:
    text = read_text(root / d / "go.mod")
    if text is None:
        return None
    m = re.search(r"(?m)^module\s+(\S+)", text)
    deps = {}
    for block in re.findall(r"(?ms)^require\s*\((.*?)\)", text):
        for line in block.splitlines():
            parts = line.split("//")[0].split()
            if len(parts) >= 2:
                deps[parts[0]] = {"spec": parts[1], "kind": "require"}
    for parts in re.findall(r"(?m)^require\s+(\S+)\s+(\S+)", text):
        deps[parts[0]] = {"spec": parts[1], "kind": "require"}
    for old, new in re.findall(r"(?m)^\s*(?:replace\s+)?(\S+)(?:\s+\S+)?\s+=>\s+(\.\.?/\S*)", text):
        if old in deps:
            deps[old]["spec"] += f" => {new}"
    gov = re.search(r"(?m)^go\s+(\S+)", text)
    return {
        "ecosystem": "go", "name": m.group(1) if m else d, "version": None,
        "private": False, "description": None, "go_version": gov.group(1) if gov else None,
        "scripts": {}, "deps": deps, "entry": {},
        "manifest": str(PurePosixPath(d, "go.mod")) if d else "go.mod",
    }


def read_python(root: Path, d: str) -> dict | None:
    t = load_toml(root / d / "pyproject.toml")
    deps: dict = {}
    name = version = desc = None
    scripts: dict = {}
    if isinstance(t, dict):
        proj = t.get("project") or {}
        poetry = (t.get("tool") or {}).get("poetry") or {}
        name = proj.get("name") or poetry.get("name")
        version = proj.get("version") or poetry.get("version")
        desc = proj.get("description") or poetry.get("description")
        for spec in proj.get("dependencies") or []:
            mm = re.match(r"\s*([A-Za-z0-9_.\-]+)(?:\[[^\]]*\])?(.*)", spec)
            if mm:
                deps[norm_py(mm.group(1))] = {"spec": mm.group(2).strip() or "*", "kind": "dependencies"}
        for group, specs in (proj.get("optional-dependencies") or {}).items():
            for spec in specs:
                mm = re.match(r"\s*([A-Za-z0-9_.\-]+)(.*)", spec)
                if mm:
                    deps.setdefault(norm_py(mm.group(1)), {"spec": mm.group(2).strip() or "*", "kind": f"extra:{group}"})
        for k, v in (poetry.get("dependencies") or {}).items():
            if k.lower() != "python":
                deps[norm_py(k)] = {"spec": v if isinstance(v, str) else json.dumps(v), "kind": "dependencies"}
        scripts = dict(proj.get("scripts") or {}) | dict(poetry.get("scripts") or {})
        for k, v in ((t.get("tool") or {}).get("uv") or {}).get("sources", {}).items():
            if isinstance(v, dict) and v.get("workspace") and norm_py(k) in deps:
                deps[norm_py(k)]["spec"] += " (workspace)"
    req = root / d / "requirements.txt"
    req_conflicts = []
    if req.exists():
        for line in (read_text(req) or "").splitlines():
            line = line.split("#")[0].strip()
            mm = re.match(r"([A-Za-z0-9_.\-]+)(?:\[[^\]]*\])?(.*)", line)
            if mm and not line.startswith("-"):
                key, spec = norm_py(mm.group(1)), mm.group(2).strip() or "*"
                if key in deps and deps[key]["kind"] != "requirements.txt" and spec != deps[key]["spec"]:
                    req_conflicts.append(f"{key}: pyproject `{deps[key]['spec']}` vs requirements.txt `{spec}`")
                deps.setdefault(key, {"spec": spec, "kind": "requirements.txt"})
    if not (t or req.exists() or (root / d / "setup.py").exists()):
        return None
    manifest = "pyproject.toml" if t else ("requirements.txt" if req.exists() else "setup.py")
    return {
        "ecosystem": "python", "name": name or (Path(d).name if d else "(root)"),
        "version": version, "private": False, "description": desc,
        "scripts": scripts, "deps": deps, "entry": {}, "manifest_conflicts": req_conflicts,
        "manifest": str(PurePosixPath(d, manifest)) if d else manifest,
    }


def read_generic(root: Path, d: str, manifest: str, eco: str) -> dict:
    return {"ecosystem": eco, "name": Path(d).name if d else "(root)", "version": None,
            "private": False, "description": None, "scripts": {}, "deps": {}, "entry": {},
            "manifest": str(PurePosixPath(d, manifest)) if d else manifest}


READERS = {"package.json": read_node, "Cargo.toml": read_cargo, "go.mod": read_go,
           "pyproject.toml": read_python, "setup.py": read_python, "requirements.txt": read_python}
GENERIC = {"pom.xml": "maven", "build.gradle": "gradle", "build.gradle.kts": "gradle",
           "composer.json": "php", "Gemfile": "ruby", "mix.exs": "elixir",
           "Package.swift": "swift", "pubspec.yaml": "dart", "deno.json": "deno",
           "CMakeLists.txt": "cmake"}
GENERIC_SUFFIX = {".csproj": "dotnet", ".fsproj": "dotnet"}


# --------------------------------------------------------------------------
# Main analysis

def analyse(root: Path, max_files: int) -> dict:
    files, truncated, method = list_files(root, max_files)
    fileset = set(files)
    dirs = {""}
    for f in files:
        parts = f.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:i]))

    # ---- language / size stats
    lang_files: Counter = Counter()
    lang_lines: Counter = Counter()
    file_lines: dict[str, int] = {}
    todo_by_file: Counter = Counter()
    todo_samples: list[str] = []
    secrets: list[dict] = []
    for f in files:
        name = f.rsplit("/", 1)[-1]
        ext = os.path.splitext(name)[1]
        lang = lang_of(name)
        if name in LOCKFILES:
            continue
        if SECRET_FILE_RE.search(f) and not SECRET_FILE_OK_RE.search(f):
            secrets.append({"file": f, "line": None, "kind": "sensitive file committed/present"})
        if lang is None and name not in ("Dockerfile", "Makefile", ".env") and not name.startswith(".env"):
            continue
        text = read_text(root / f)
        if text is None:
            continue
        n = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
        if lang:
            lang_files[lang] += 1
            lang_lines[lang] += n
            file_lines[f] = n
        minified = name.endswith((".min.js", ".min.css")) or (n and len(text) / max(n, 1) > 500)
        if minified:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if lang and lang not in NON_CODE_LANGS and TODO_RE.search(line):
                todo_by_file[f] += 1
                if len(todo_samples) < 25:
                    todo_samples.append(f"{f}:{i}: {line.strip()[:120]}")
            if len(line) > 400:
                continue
            for kind, rx in SECRET_PATTERNS:
                m = rx.search(line)
                if m and not PLACEHOLDER_RE.search(m.group(0)):
                    secrets.append({"file": f, "line": i, "kind": kind,
                                    "match": m.group(0)[:6] + "…(masked)"})
                    break

    code_files = [f for f in file_lines if lang_of(f) not in NON_CODE_LANGS]
    test_files = [f for f in code_files if is_test_path(f) or (
        f.endswith(".rs") and "#[cfg(test)]" in (read_text(root / f) or ""))]

    # ---- markers
    markers: dict[str, list[str]] = defaultdict(list)
    for f in files:
        name = f.rsplit("/", 1)[-1]
        if name in MARKERS:
            markers[MARKERS[name]].append(f)
        elif name.endswith((".csproj", ".fsproj", ".sln")):
            markers[".NET"].append(f)
        elif name.endswith(".tf"):
            markers.setdefault("Terraform", []).append(f)
        elif name.startswith("Dockerfile") or name.endswith(".Dockerfile"):
            markers["Docker"].append(f)
    ci = sorted({f for f in files for g in CI_GLOBS if fnmatch.fnmatchcase(f, g)})
    if ci:
        markers["CI workflows"] = ci
    if "Terraform" in markers and len(markers["Terraform"]) > 8:
        tf_dirs = sorted({str(PurePosixPath(f).parent) for f in markers["Terraform"]})
        markers["Terraform"] = [f"{d}/ (*.tf)" for d in tf_dirs]

    # ---- packages: every directory with a recognised manifest
    packages: dict[str, dict] = {}
    for f in files:
        d, _, name = f.rpartition("/")
        reader = READERS.get(name)
        info = None
        if reader:
            if d in packages and name in ("requirements.txt", "setup.py") and packages[d]["ecosystem"] == "python":
                continue
            info = reader(root, d)
        elif name in GENERIC:
            info = read_generic(root, d, name, GENERIC[name])
        elif os.path.splitext(name)[1] in GENERIC_SUFFIX:
            info = read_generic(root, d, name, GENERIC_SUFFIX[os.path.splitext(name)[1]])
        if info is None:
            continue
        key = d if d not in packages or packages[d]["ecosystem"] == info["ecosystem"] else f"{d}#{info['ecosystem']}"
        info["path"] = d or "."
        packages[key] = info

    fixture_packages = sorted(p["path"] for k, p in packages.items() if FIXTURE_RE.search(p["path"]))
    packages = {k: p for k, p in packages.items() if not FIXTURE_RE.search(p["path"])}
    for p in packages.values():
        p["kind"] = "example" if EXAMPLE_RE.search(p["path"]) else "package"

    # ---- workspace declarations
    workspaces: list[dict] = []
    problems: list[str] = []

    def add_ws(kind: str, source: str, patterns: list[str], eco: str):
        matched, unmatched = glob_dirs(root, patterns, dirs)
        with_manifest = [m for m in matched if any(
            k == m or k.startswith(m + "#") for k in packages) and packages.get(m, {}).get("ecosystem", eco) in (eco, None)]
        workspaces.append({"tool": kind, "declared_in": source, "patterns": patterns,
                           "members": with_manifest})
        for u in unmatched:
            problems.append(f"{source}: workspace pattern `{u}` matches no directory")
        for m in matched:
            if m not in with_manifest and not any(k.startswith(m + "#") for k in packages):
                problems.append(f"{source}: workspace member `{m}` has no {eco} manifest")
        return with_manifest

    root_pj = load_json(root / "package.json") if "package.json" in fileset else None
    if isinstance(root_pj, dict) and root_pj.get("workspaces"):
        ws = root_pj["workspaces"]
        pats = ws if isinstance(ws, list) else ws.get("packages", [])
        add_ws("npm/yarn/bun workspaces", "package.json", pats, "node")
    if "pnpm-workspace.yaml" in fileset:
        add_ws("pnpm workspace", "pnpm-workspace.yaml",
               yaml_list(read_text(root / "pnpm-workspace.yaml") or "", "packages"), "node")
    if "lerna.json" in fileset:
        lj = load_json(root / "lerna.json") or {}
        if lj.get("packages"):
            add_ws("Lerna", "lerna.json", lj["packages"], "node")
    if "rush.json" in fileset:
        rj = load_json(root / "rush.json") or {}
        add_ws("Rush", "rush.json", [p.get("projectFolder", "") for p in rj.get("projects", [])], "node")
    project_jsons = [f for f in files if f.endswith("/project.json") or f == "project.json"]
    if "nx.json" in fileset or project_jsons:
        workspaces.append({"tool": "Nx", "declared_in": "nx.json" if "nx.json" in fileset else "project.json files",
                           "patterns": [], "members": sorted(str(PurePosixPath(p).parent) for p in project_jsons)})
    if "turbo.json" in fileset:
        tj = load_json(root / "turbo.json") or {}
        tasks = list((tj.get("tasks") or tj.get("pipeline") or {}).keys())
        workspaces.append({"tool": "Turborepo (task runner)", "declared_in": "turbo.json",
                           "patterns": [], "members": [], "tasks": tasks})
    root_cargo = load_toml(root / "Cargo.toml") if "Cargo.toml" in fileset else None
    if isinstance(root_cargo, dict) and "workspace" in root_cargo:
        w = root_cargo["workspace"]
        members = add_ws("Cargo workspace", "Cargo.toml", list(w.get("members", [])), "cargo")
        excl = set(w.get("exclude", []))
        for k, p in packages.items():
            if p["ecosystem"] == "cargo" and p["path"] not in (".", *members) and p["path"] not in excl:
                problems.append(f"Cargo.toml: crate `{p['path']}` is not a workspace member (nor excluded)")
    if "go.work" in fileset:
        text = read_text(root / "go.work") or ""
        uses = []
        for block in re.findall(r"(?ms)^use\s*\((.*?)\)", text):
            uses += [l.split("//")[0].strip() for l in block.splitlines() if l.split("//")[0].strip()]
        uses += re.findall(r"(?m)^use\s+(\S+)\s*$", text)
        uses = [u.strip("./") if u not in (".", "./") else "" for u in uses]
        members = add_ws("Go workspace", "go.work", uses or [""], "go")
        for k, p in packages.items():
            if p["ecosystem"] == "go" and (p["path"] if p["path"] != "." else "") not in members:
                problems.append(f"go.work: module `{p['path']}` ({p['name']}) is not listed in go.work")
    root_py = load_toml(root / "pyproject.toml") if "pyproject.toml" in fileset else None
    if isinstance(root_py, dict):
        uvw = ((root_py.get("tool") or {}).get("uv") or {}).get("workspace")
        if uvw:
            add_ws("uv workspace", "pyproject.toml", list(uvw.get("members", [])), "python")
        poetry_pk = ((root_py.get("tool") or {}).get("poetry") or {}).get("packages")
        if poetry_pk and any(isinstance(x, dict) and x.get("from") for x in poetry_pk):
            pass
    for sg in ("settings.gradle", "settings.gradle.kts"):
        if sg in fileset:
            text = read_text(root / sg) or ""
            incs = re.findall(r"""include\s*\(?\s*((?:['"][^'"]+['"]\s*,?\s*)+)""", text)
            mods = [m.strip(":").replace(":", "/") for grp in incs for m in re.findall(r"['\"]([^'\"]+)['\"]", grp)]
            workspaces.append({"tool": "Gradle multi-project", "declared_in": sg, "patterns": mods, "members": mods})
    if "pom.xml" in fileset:
        mods = re.findall(r"<module>([^<]+)</module>", read_text(root / "pom.xml") or "")
        if mods:
            workspaces.append({"tool": "Maven multi-module", "declared_in": "pom.xml", "patterns": mods, "members": mods})
    for b in ("WORKSPACE", "WORKSPACE.bazel", "MODULE.bazel"):
        if b in fileset:
            builds = [f for f in files if f.rsplit("/", 1)[-1] in ("BUILD", "BUILD.bazel")]
            workspaces.append({"tool": "Bazel", "declared_in": b, "patterns": [],
                               "members": sorted({str(PurePosixPath(f).parent) for f in builds})[:200]})
            break

    # ---- per-package stats
    pkg_dirs = sorted({p["path"] for p in packages.values()}, key=lambda d: (-len(d), d))
    owner: dict[str, str] = {}
    for f in files:
        for d in pkg_dirs:
            if under(f, "" if d == "." else d):
                owner[f] = d
                break
    for p in packages.values():
        mine = [f for f, d in owner.items() if d == p["path"]]
        code = [f for f in mine if f in file_lines and lang_of(f) not in NON_CODE_LANGS]
        langs = Counter(lang_of(f) for f in code)
        p["files"] = len(mine)
        p["code_lines"] = sum(file_lines[f] for f in code)
        p["languages"] = dict(langs.most_common(3))
        p["test_files"] = sum(1 for f in code if is_test_path(f) or (
            f.endswith(".rs") and "#[cfg(test)]" in (read_text(root / f) or "")))
        if p["ecosystem"] == "go":
            mains = sorted({str(PurePosixPath(f).parent) for f in code if f.endswith(".go")
                            and re.search(r"(?m)^package main\b", read_text(root / f) or "")})
            if mains:
                p["entry"]["main packages"] = mains[:10]
        if p["ecosystem"] == "python":
            mains = [f for f in code if f.endswith(".py") and "__main__" in (read_text(root / f) or "")
                     and re.search(r"if __name__ ==", read_text(root / f) or "")]
            if mains:
                p["entry"]["__main__ scripts"] = mains[:10]
        if p["ecosystem"] == "cargo":
            bins = sorted(f for f in code if re.match(rf"^{re.escape('' if p['path']=='.' else p['path']+'/')}src/bin/[^/]+\.rs$", f))
            if bins:
                p["entry"]["bins"] = bins

    # ---- internal dependency graph
    by_name: dict[tuple[str, str], str] = {}
    for k, p in packages.items():
        by_name[(p["ecosystem"], norm_py(p["name"]) if p["ecosystem"] == "python" else p["name"])] = k
    edges: list[tuple[str, str, str]] = []
    for k, p in packages.items():
        for dep, meta in p["deps"].items():
            tgt = by_name.get((p["ecosystem"], dep))
            if tgt and p["ecosystem"] == "node" and not _links_locally(meta["spec"], packages[tgt].get("version")):
                tgt = None  # same name as a local package, but resolves from the registry
            if tgt and tgt != k:
                edges.append((k, tgt, meta["spec"]))
                meta["internal"] = True
    graph: dict[str, set[str]] = defaultdict(set)
    for a, b, _ in edges:
        graph[a].add(b)

    cycles: list[list[str]] = []
    seen_cycles: set[frozenset] = set()

    def dfs(node, stack, onstack, visited):
        visited.add(node)
        stack.append(node)
        onstack.add(node)
        for nxt in sorted(graph.get(node, ())):
            if nxt in onstack:
                cyc = stack[stack.index(nxt):] + [nxt]
                key = frozenset(cyc)
                if key not in seen_cycles:
                    seen_cycles.add(key)
                    cycles.append(cyc)
            elif nxt not in visited:
                dfs(nxt, stack, onstack, visited)
        stack.pop()
        onstack.discard(node)

    visited: set[str] = set()
    for n in sorted(graph):
        if n not in visited:
            dfs(n, [], set(), visited)

    depended_on = Counter(b for _, b, _ in edges)

    # ---- external version drift (same dep, different specs, same ecosystem)
    drift = []
    by_dep: dict[tuple[str, str], dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for k, p in packages.items():
        if p.get("kind") == "example":
            continue
        for dep, meta in p["deps"].items():
            if meta.get("internal") or meta["spec"].startswith(("workspace", "path:")):
                continue
            by_dep[(p["ecosystem"], dep)][meta["spec"]].append(p["path"])
    for (eco, dep), specs in sorted(by_dep.items()):
        if len(specs) > 1:
            drift.append({"ecosystem": eco, "dependency": dep, "versions": dict(specs)})
    drift.sort(key=lambda d: (-sum(len(v) for v in d["versions"].values()), d["dependency"]))

    # ---- internal deps declared with a version that doesn't match the target's
    internal_mismatch = []
    for a, b, spec in edges:
        tv = packages[b].get("version")
        if packages[a]["ecosystem"] == "node" and tv and not spec.startswith(("workspace:", "file:", "link:", "*")):
            nums = re.findall(r"\d+", spec)
            if nums and nums[0] != re.findall(r"\d+", tv)[0]:
                internal_mismatch.append(f"{packages[a]['name']} wants {packages[b]['name']}@{spec} but it is {tv}")

    # ---- build/run risks: cheap static checks for "this won't build or ship as committed"
    build_risks: list[str] = []
    names = {f.rsplit("/", 1)[-1] for f in files}
    ci_text = "\n".join(read_text(root / f) or "" for f in ci)
    node_pkgs = [p for p in packages.values() if p["ecosystem"] == "node"]
    if node_pkgs and not names & {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock"}:
        frozen = [f for f in ci + markers.get("Docker", []) if re.search(
            r"--frozen-lockfile|--immutable|npm ci\b", read_text(root / f) or "")]
        build_risks.append("No JS lockfile committed" + (
            f"; `--frozen-lockfile`/`npm ci` in {', '.join(frozen)} will fail" if frozen else ""))
    for p in node_pkgs:
        d = "" if p["path"] == "." else p["path"]
        uses_tsc = any(re.search(r"\btsc\b", str(v)) for v in p["scripts"].values())
        has_tsconfig = any(f"{d}/tsconfig.json".lstrip("/") == f or f == "tsconfig.json" or
                           re.match(rf"^{re.escape(d)}/tsconfig[^/]*\.json$", f) for f in fileset)
        if uses_tsc and not has_tsconfig:
            build_risks.append(f"`{p['path']}` runs `tsc` but no tsconfig.json exists there or at the root")
    for p in packages.values():
        d = "" if p["path"] == "." else p["path"]
        if p["ecosystem"] == "go" and any(m["kind"] == "require" and "=>" not in m["spec"] for m in p["deps"].values()) \
                and str(PurePosixPath(d, "go.sum")).lstrip("./") not in fileset and f"{d}/go.sum".lstrip("/") not in fileset:
            build_risks.append(f"`{p['path']}` has external Go requires but no go.sum (builds fail outside a warm module cache)")
    if any(p["ecosystem"] == "cargo" and p["entry"].get("bin") for p in packages.values()) and "Cargo.lock" not in names:
        build_risks.append("Cargo binaries but no Cargo.lock committed (non-reproducible builds)")
    for f in markers.get("Docker", []):
        if FIXTURE_RE.search(f) or is_test_path(f):
            continue
        text = read_text(root / f) or ""
        ctx = str(PurePosixPath(f).parent)
        ctx = "" if ctx == "." else ctx
        parts = ctx.split("/") if ctx else []
        ancestors = ["/".join(parts[:i]) for i in range(len(parts), -1, -1)]
        has_ignore = any(f"{a}/.dockerignore".lstrip("/") in fileset or
                         f"{f}.dockerignore" in fileset for a in ancestors)
        if re.search(r"(?m)^\s*(COPY|ADD)\s+(--\S+\s+)*\.\s+\S+", text) and not has_ignore:
            leaked = [x for x in fileset if SECRET_FILE_RE.search(x) and not SECRET_FILE_OK_RE.search(x)
                      and not FIXTURE_RE.search(x) and not is_test_path(x)]
            build_risks.append(f"`{f}` copies the whole build context with no .dockerignore"
                               + (f" — this bakes {', '.join(sorted(leaked)[:3])} into the image" if leaked else ""))
    for f in markers.get("Docker Compose", []):
        text = read_text(root / f) or ""
        for m in re.finditer(r"context:\s*['\"]?([^'\",}\s]+)", text):
            c = m.group(1).strip("./") if m.group(1) not in (".", "./") else ""
            seg = text[m.end(): m.end() + 200]
            df = re.search(r"dockerfile:\s*['\"]?([^'\",}\s]+)", seg)
            want = str(PurePosixPath(c or ".", df.group(1))) if df else str(PurePosixPath(c or ".", "Dockerfile"))
            want = want[2:] if want.startswith("./") else want
            if want not in fileset and not df:
                build_risks.append(f"`{f}` builds context `{m.group(1)}` but there is no Dockerfile at `{want}`")
    if ci:
        eco_ci = {"node": r"\b(npm|pnpm|yarn|bun|npx|node)\b", "cargo": r"\bcargo\b", "go": r"\bgo (build|test|vet)\b",
                  "python": r"\b(pytest|python|pip|uv|poetry|tox|ruff)\b", "maven": r"\bmvn\b", "gradle": r"\bgradlew?\b"}
        for eco in sorted({p["ecosystem"] for p in packages.values()}):
            rx = eco_ci.get(eco)
            if rx and not re.search(rx, ci_text):
                where = ", ".join(sorted(p["path"] for p in packages.values() if p["ecosystem"] == eco)[:5])
                build_risks.append(f"CI never builds/tests the {eco} code ({where})")
        if "turbo.json" in fileset:
            tj = load_json(root / "turbo.json") or {}
            tdefs = tj.get("tasks") or tj.get("pipeline") or {}
            tasks = list(tdefs.keys())
            def _name(t):  # "pkg#build" / "^build" / "build" -> "build"
                return t.lstrip("^").split("#")[-1]
            reached = {t for t in tasks if re.search(rf"\b{re.escape(_name(t))}\b", ci_text)}
            frontier = list(reached)
            while frontier:
                t = frontier.pop()
                for d in (tdefs.get(t) or {}).get("dependsOn", []) if isinstance(tdefs.get(t), dict) else []:
                    for cand in tasks:
                        if _name(cand) == _name(d) and cand not in reached:
                            reached.add(cand); frontier.append(cand)
            missing = [t for t in tasks if _name(t) not in ("dev",) and t not in reached
                       and not (isinstance(tdefs.get(t), dict) and tdefs[t].get("persistent"))]
            if missing:
                build_risks.append(f"turbo tasks never run in CI: {', '.join(missing)}")
    elif packages:
        build_risks.append("No CI configuration found")

    # ---- git
    git = None
    top = (run_git(root, "rev-parse", "--show-toplevel") or "").strip()
    if top:
        scope = ["--", "."]  # keep history scoped to the inspected directory
        count = (run_git(root, "rev-list", "--count", "HEAD", *scope) or "").strip()
        first = (run_git(root, "log", "--reverse", "--format=%as", *scope) or "").split("\n")[0]
        last = (run_git(root, "log", "-1", "--format=%as", *scope) or "").strip()
        authors = run_git(root, "shortlog", "-sn", "--no-merges", "HEAD", *scope) or ""
        churn_raw = run_git(root, "log", "--since=12.months", "--format=", "--name-only",
                            "--relative", *scope, timeout=120) or ""
        churn = Counter(l for l in churn_raw.splitlines() if l and l in fileset).most_common(10)
        branch = (run_git(root, "rev-parse", "--abbrev-ref", "HEAD") or "").strip()
        status = run_git(root, "status", "--porcelain", "--", ".") or ""
        is_sub = Path(top).resolve() != root.resolve()
        git = {"branch": branch, "commits": int(count) if count.isdigit() else None,
               "first_commit": first or None, "last_commit": last or None,
               "contributors": len([l for l in authors.splitlines() if l.strip()]),
               "top_contributors": [l.strip() for l in authors.splitlines()[:5]],
               "churn_12mo": churn, "uncommitted_changes": len(status.splitlines()),
               "subdirectory_of": top if is_sub else None}

    # ---- shape
    real_pkgs = [p for p in packages.values()]
    declared = [w for w in workspaces if w["members"] or w["tool"].startswith("Turborepo")]
    multi_dirs = {p["path"] for p in real_pkgs if p["path"] != "."}
    if declared and multi_dirs:
        shape = "monorepo (declared workspaces)"
    elif len(multi_dirs) >= 2:
        shape = "multi-project repo (several manifests, no workspace tool)"
    elif multi_dirs and not any(p["path"] == "." for p in real_pkgs):
        shape = "single project in a subdirectory"
    else:
        shape = "single project"
    eco_count = Counter(p["ecosystem"] for p in real_pkgs)
    if len(eco_count) > 1:
        shape += f", polyglot ({', '.join(f'{e}×{n}' for e, n in eco_count.most_common())})"

    readmes = sorted(f for f in files if re.search(r"(^|/)readme(\.[a-z]+)?$", f, re.I))
    docs = sorted({f.split("/")[0] for f in files if f.split("/")[0].lower() in ("docs", "doc", "documentation", "adr", "adrs")})
    agent_docs = sorted(f for f in files if f.rsplit("/", 1)[-1] in
                        ("CLAUDE.md", "AGENTS.md", "CONTRIBUTING.md", "ARCHITECTURE.md", ".cursorrules", "copilot-instructions.md"))

    top_dirs = Counter()
    for f in files:
        top_dirs[f.split("/")[0] + ("/" if "/" in f else "")] += 1

    return {
        "root": str(root.resolve()), "listing_method": method, "truncated": truncated,
        "shape": shape,
        "totals": {"files": len(files), "code_files": len(code_files),
                   "code_lines": sum(file_lines[f] for f in code_files),
                   "test_files": len(test_files)},
        "languages": [{"language": l, "files": lang_files[l], "lines": lang_lines[l]}
                      for l, _ in lang_lines.most_common()],
        "top_level": top_dirs.most_common(40),
        "markers": {k: sorted(v)[:25] for k, v in sorted(markers.items())},
        "workspaces": workspaces,
        "workspace_problems": problems,
        "packages": sorted(packages.values(), key=lambda p: p["path"]),
        "internal_edges": [{"from": packages[a]["path"], "to": packages[b]["path"], "spec": s} for a, b, s in edges],
        "cycles": [[packages[n]["path"] for n in c] for c in cycles],
        "not_depended_on": sorted(p["path"] for k, p in packages.items()
                                  if depended_on[k] == 0 and len(packages) > 1 and p["path"] != "."
                                  and p.get("kind") != "example"),
        "most_depended_on": [(packages[k]["path"], n) for k, n in depended_on.most_common(12)],
        "fixture_packages": fixture_packages,
        "version_drift": drift,
        "build_risks": build_risks,
        "internal_version_mismatch": internal_mismatch,
        "largest_files": sorted(((n, f) for f, n in file_lines.items()
                                 if lang_of(f) not in NON_CODE_LANGS),
                                reverse=True)[:12],
        "todo_total": sum(todo_by_file.values()),
        "todo_top_files": todo_by_file.most_common(8),
        "todo_samples": todo_samples,
        "possible_secrets": secrets[:40],
        "readmes": readmes[:30], "docs_dirs": docs, "agent_docs": agent_docs,
        "git": git,
    }


# --------------------------------------------------------------------------
# Markdown rendering

def md(inv: dict) -> str:
    o: list[str] = []
    w = o.append
    t = inv["totals"]
    w(f"# Inventory: `{inv['root']}`\n")
    w(f"- **Shape:** {inv['shape']}")
    w(f"- **Files:** {t['files']} ({inv['listing_method']}{', TRUNCATED' if inv['truncated'] else ''}); "
      f"code files {t['code_files']}, code lines {t['code_lines']:,}, test files {t['test_files']}")
    if inv["git"]:
        g = inv["git"]
        w(f"- **Git:** branch `{g['branch']}`, {g['commits']} commits, {g['first_commit']} → {g['last_commit']}, "
          f"{g['contributors']} contributors, {g['uncommitted_changes']} uncommitted changes"
          + (f" (history scoped to this subdirectory of `{g['subdirectory_of']}`)" if g.get("subdirectory_of") else ""))
    else:
        w("- **Git:** not a git repository (no history signals)")
    w("\n## Languages (by lines)\n")
    w("| Language | Files | Lines |\n|---|---:|---:|")
    for l in inv["languages"][:12]:
        w(f"| {l['language']} | {l['files']} | {l['lines']:,} |")
    w("\n## Top-level layout\n")
    w(", ".join(f"`{d}` ({n})" for d, n in inv["top_level"]))
    w("\n## Tooling markers\n")
    for k, v in inv["markers"].items():
        w(f"- **{k}:** " + ", ".join(f"`{x}`" for x in v[:5]) + (f" … (+{len(v) - 5})" if len(v) > 5 else ""))
    if inv["workspaces"]:
        w("\n## Workspaces\n")
        for ws in inv["workspaces"]:
            extra = f"; tasks: {', '.join(ws['tasks'])}" if ws.get("tasks") else ""
            w(f"- **{ws['tool']}** (`{ws['declared_in']}`): patterns {ws['patterns'] or '—'} → "
              f"{len(ws['members'])} members{extra}")
    if inv["workspace_problems"]:
        w("\n### Workspace problems\n")
        for p in inv["workspace_problems"][:20]:
            w(f"- {p}")
        if len(inv["workspace_problems"]) > 20:
            w(f"- … and {len(inv['workspace_problems']) - 20} more (see JSON)")
    examples = [p for p in inv["packages"] if p.get("kind") == "example"]
    core = [p for p in inv["packages"] if p.get("kind") != "example"]
    w(f"\n## Packages / projects ({len(core)}" + (f" + {len(examples)} examples" if examples else "") + ")\n")
    if inv.get("fixture_packages"):
        fx = Counter("/".join(x.split("/")[:2]) for x in inv["fixture_packages"])
        w(f"Ignored {len(inv['fixture_packages'])} test-fixture manifests (under "
          + ", ".join(f"`{d}/`" for d, _ in fx.most_common(5)) + ").\n")
    if examples:
        ex_dirs = Counter(x["path"].split("/")[0] for x in examples)
        w(f"Example/template packages ({len(examples)}, excluded from drift checks): "
          + ", ".join(f"`{d}/` ({n})" for d, n in ex_dirs.most_common(5)) + "\n")
    w("| Path | Name | Eco | Version | Code lines | Tests | Main langs | Scripts / entry |\n|---|---|---|---|---:|---:|---|---|")
    shown = core
    if len(shown) > 40:
        shown = sorted(shown, key=lambda p: -p["code_lines"])[:40]
        w(f"| … | showing the 40 largest of {len(core)}; full list in the JSON | | | | | | |")
    for p in sorted(shown, key=lambda p: p["path"]):
        scripts = ", ".join(list(p["scripts"])[:6])
        entry = ", ".join(f"{k}" for k in p["entry"])
        w(f"| `{p['path']}` | {p['name']} | {p['ecosystem']} | {p.get('version') or ''} | {p['code_lines']:,} | "
          f"{p['test_files']} | {', '.join(p['languages'])} | {'; '.join(x for x in (scripts, entry) if x)} |")
    if inv["internal_edges"]:
        w(f"\n## Internal dependency graph ({len(inv['internal_edges'])} edges)\n")
        ids = {p["path"]: f"n{i}" for i, p in enumerate(inv["packages"])}
        linked = {e["from"] for e in inv["internal_edges"]} | {e["to"] for e in inv["internal_edges"]}
        if len(linked) <= 30:
            w("```mermaid\ngraph LR")
            for p in inv["packages"]:
                if p["path"] in linked or (p["path"] != "." and p.get("kind") != "example"):
                    w(f'  {ids[p["path"]]}["{p["name"]}"]')
            for e in inv["internal_edges"]:
                w(f"  {ids[e['from']]} --> {ids[e['to']]}")
            w("```")
        else:
            w(f"{len(linked)} packages are linked — too many to draw; full edge list in the JSON. "
              "Most depended-on (the core everything builds on): "
              + ", ".join(f"`{p}` ({n})" for p, n in inv.get("most_depended_on", [])[:12]))
        if inv["cycles"]:
            w("\n**Dependency cycles:** " + "; ".join(" → ".join(f"`{n}`" for n in c) for c in inv["cycles"]))
        if inv["not_depended_on"]:
            nd = inv["not_depended_on"]
            w(f"\n**Not depended on by any other package** ({len(nd)}; apps/tools, or possibly dead): "
              + ", ".join(f"`{x}`" for x in nd[:30]) + (f" … (+{len(nd) - 30})" if len(nd) > 30 else ""))
    conflicts = [(p["path"], c) for p in inv["packages"] for c in p.get("manifest_conflicts") or []]
    if conflicts:
        w(f"\n## Conflicting pins between manifests of one project ({len(conflicts)})\n")
        for path, c in conflicts[:25]:
            w(f"- `{path}`: {c}")
    if inv["internal_version_mismatch"]:
        w("\n**Internal version mismatches:** " + "; ".join(inv["internal_version_mismatch"]))
    if inv["version_drift"]:
        w(f"\n## External dependency version drift ({len(inv['version_drift'])})\n")
        if len(inv["version_drift"]) > 12:
            w(f"Showing the 12 most widespread; full list in the JSON.\n")
        for d in inv["version_drift"][:12]:
            w(f"- `{d['dependency']}` ({d['ecosystem']}): " +
              "; ".join(f"`{s}` in {', '.join(f'`{x}`' for x in ps)}" for s, ps in d["versions"].items()))
    if inv["build_risks"]:
        w(f"\n## Build / ship risks ({len(inv['build_risks'])}) — static checks, confirm by reading\n")
        for r in inv["build_risks"]:
            w(f"- {r}")
    w("\n## Hotspots\n")
    w("Largest code files: " + ", ".join(f"`{f}` ({n})" for n, f in inv["largest_files"][:8]))
    w(f"\nTODO/FIXME/HACK markers: {inv['todo_total']}" +
      (" — most in " + ", ".join(f"`{f}` ({n})" for f, n in inv["todo_top_files"][:5]) if inv["todo_total"] else ""))
    if inv["git"] and inv["git"]["churn_12mo"]:
        w("\nMost-changed files (12 months): " + ", ".join(f"`{f}` ({n})" for f, n in inv["git"]["churn_12mo"][:8]))
    if inv["possible_secrets"]:
        w(f"\n## Possible secrets ({len(inv['possible_secrets'])}) — verify by reading; values masked\n")
        def _is_fixture(s):
            return is_test_path(s["file"]) or bool(re.search(
                r"(^|/)(docs?|examples?|fixtures?|testdata)(/|$)|example", s["file"], re.I))
        ordered = sorted(inv["possible_secrets"], key=_is_fixture)
        for s in ordered[:15]:
            loc = f"{s['file']}:{s['line']}" if s["line"] else s["file"]
            fixture = " — in a test/example/docs file, likely a fixture" if _is_fixture(s) else ""
            w(f"- `{loc}` — {s['kind']}" + (f" (`{s['match']}`)" if s.get("match") else "") + fixture)
    w("\n## Docs\n")
    w("READMEs: " + (", ".join(f"`{r}`" for r in inv["readmes"][:12]) or "none"))
    if inv["docs_dirs"]:
        w("\nDocs dirs: " + ", ".join(f"`{d}/`" for d in inv["docs_dirs"]))
    if inv["agent_docs"]:
        w("\nContributor/agent docs: " + ", ".join(f"`{d}`" for d in inv["agent_docs"]))
    return "\n".join(o) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--json", help="also write the full inventory as JSON to this path")
    ap.add_argument("--max-files", type=int, default=150_000)
    a = ap.parse_args()
    root = Path(a.root)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    inv = analyse(root, a.max_files)
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(inv, indent=2, default=str))
    sys.stdout.write(md(inv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
