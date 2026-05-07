# 🤝 Contributing to SysWatch Pro

Thank you for considering contributing to **SysWatch Pro**! This document explains our workflow, standards, and how to get your changes merged.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Branch Strategy (Gitflow)](#branch-strategy-gitflow)
- [Conventional Commits](#conventional-commits)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [CI Requirements](#ci-requirements)

---

## Code of Conduct

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Branch Strategy (Gitflow)

We follow a **Gitflow** branching model:

```
main          ← Production-ready code only. Protected. Requires PR + 1 reviewer.
└── dev       ← Integration branch. Staging deploys from here.
    └── feature/<ticket>-short-description   ← Your work goes here
    └── fix/<ticket>-short-description
    └── chore/<ticket>-short-description
```

### Rules

| Branch | Purpose | Direct Push? |
|--------|---------|-------------|
| `main` | Production releases | ❌ Never |
| `dev` | Staging integration | ❌ Never |
| `feature/*` | New features | ✅ Your own branches |
| `fix/*` | Bug fixes | ✅ Your own branches |
| `chore/*` | Maintenance | ✅ Your own branches |

### Workflow

```bash
# 1. Sync with latest dev
git checkout dev
git pull origin dev

# 2. Create your branch
git checkout -b feature/42-add-prometheus-metrics

# 3. Make your changes, then commit (see Conventional Commits below)
git add .
git commit -m "feat: add prometheus metrics endpoint"

# 4. Push and open PR → dev
git push origin feature/42-add-prometheus-metrics
```

---

## Conventional Commits

We enforce **Conventional Commits** — this feeds automatic changelog generation.

### Format

```
<type>[optional scope]: <short description>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to Use |
|------|------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `chore` | Build process, tooling, dependencies |
| `docs` | Documentation only |
| `refactor` | Code change that isn't a fix or feature |
| `test` | Adding or updating tests |
| `ci` | CI/CD pipeline changes |
| `perf` | Performance improvement |
| `style` | Formatting, missing semicolons — no logic change |

### Examples

```bash
git commit -m "feat: add real-time CPU heatmap to metrics view"
git commit -m "fix: resolve crash when no services are connected"
git commit -m "chore: bump PySide6 from 6.6.1 to 6.7.0"
git commit -m "docs: update README with Docker deployment guide"
git commit -m "feat!: redesign settings API"  # BREAKING CHANGE — note the !
```

> ⚠️ PRs with non-conventional commit messages **will not be merged**.

---

## Development Setup

### Prerequisites

- Python 3.10+
- Git

### Steps

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/syswatch.git
cd syswatch

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/macOS

# 3. Install all dependencies (including dev tools)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Install pre-commit hooks (runs lint/format on every commit)
pre-commit install

# 5. Run tests to verify setup
pytest tests/ -v
```

---

## Pull Request Process

1. **Branch** from `dev`, not from `main`
2. **Fill out** the PR template completely
3. **Ensure CI passes** — all green checks required
4. **Request review** from at least 1 maintainer
5. **Squash merge** is preferred for feature branches
6. **Delete your branch** after merge

### PR → `dev` (Staging)
- 1 reviewer required
- All CI checks must pass (lint, format, test, coverage ≥ 80%)

### PR → `main` (Production)
- 2 reviewers required
- All CI checks must pass
- Manual approval from a maintainer via GitHub Environments

---

## CI Requirements

Every PR must pass all of the following:

| Check | Tool | Threshold |
|-------|------|-----------|
| Linting | `ruff` | Zero errors |
| Formatting | `black --check` | Zero diffs |
| Tests | `pytest` | All pass |
| Coverage | `pytest-cov` | ≥ 80% |
| Security | `Snyk` + `Trivy` | No HIGH/CRITICAL |
| Code Quality | SonarCloud | Quality Gate pass |

---

## Questions?

Open a [GitHub Discussion](https://github.com/AKash-A007/syswatch/discussions) or ping us in the issue tracker.
