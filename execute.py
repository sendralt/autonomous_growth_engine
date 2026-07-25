"""User-triggered setup script for the Autonomous Growth Engine plugin.

Creates the full directory structure and copies the dashboard template
into the configured growth docs path.
"""
import os
import sys


def _resolve_growth_dir() -> str:
    """Resolve the growth directory using plugin config defaults."""
    try:
        from helpers.plugins import get_plugin_config
        config = get_plugin_config("autonomous_growth_engine") or {}
    except Exception:
        config = {}

    raw_path = str(config.get("growth_docs_path", "docs/growth") or "docs/growth").strip()

    if os.path.isabs(raw_path):
        return os.path.abspath(raw_path)

    # Best-effort workdir resolution
    try:
        from agent import AgentContext
        ctx = AgentContext.get()
        if ctx and getattr(ctx, "workdir", None):
            workdir = ctx.workdir
        else:
            workdir = os.path.abspath("/a0/usr/workdir")
    except Exception:
        workdir = os.path.abspath("/a0/usr/workdir")

    return os.path.abspath(os.path.join(workdir, raw_path))


DASHBOARD_TEMPLATE = """# Growth Dashboard

> Last updated: AUTO-UPDATED BY GROWTH SYSTEM
> Status: Active - Autonomous Engine Running

---

## Key Metrics (Update Monthly)

| Metric | Current | Last Month | Target | Trend |
|---|---|---|---|---|
| Total installs/users | -- | -- | -- | -- |
| Paying customers | -- | -- | -- | -- |
| MRR | -- | -- | -- | -- |
| Email list size | -- | -- | -- | -- |
| Blog posts published | 0 | -- | 2/month | -- |
| Social posts published | 0 | -- | 3/week | -- |
| Influencers contacted | 0 | -- | 5/week | -- |
| Community posts | 0 | -- | 2/week | -- |

---

## Content Pipeline

### Blog Posts
| Title | Status | Date Created | Keywords |
|---|---|---|---|
| -- | -- | -- | -- |

### Social Media
| Week Of | Platform | Content Type | Status |
|---|---|---|---|
| -- | -- | -- | -- |

### Email
| Email | Status | Send Date | Open Rate |
|---|---|---|---|
| -- | -- | -- | -- |

---

## Influencer Pipeline

| Creator | Platform | Followers | Status | Date Contacted | Response | Content Posted |
|---|---|---|---|---|---|---|
| -- | -- | -- | -- | -- | -- | -- |

---

## Directory and Backlink Tracker

| Directory | Date Submitted | Status | Live URL |
|---|---|---|---|
| -- | -- | -- | -- |

---

## Research Reports

| Report | Date | Key Findings |
|---|---|---|
| -- | -- | -- |

---

## Human Review Queue

> Items below need human review. Approve, edit, or reject.

| Item | Type | Path | Date Created | Priority |
|---|---|---|---|---|
| -- | -- | -- | -- | -- |

---

## Action Items for Human

1. [ ] --
2. [ ] --
3. [ ] --

---

## Monthly Growth Review

| Month | Customers | Revenue | Key Win | Key Challenge | Strategy Adjustment |
|---|---|---|---|---|---|
| -- | -- | -- | -- | -- | -- |
"""


REQUIRED_DIRS = [
    os.path.join("review", "blog"),
    os.path.join("review", "social"),
    os.path.join("review", "reddit"),
    os.path.join("review", "email"),
    os.path.join("review", "influencer"),
    os.path.join("research", "competitor-watch"),
    os.path.join("research", "trend-reports"),
    os.path.join("research", "keyword-research"),
    "pipeline",
    "published",
]


def main():
    growth_dir = _resolve_growth_dir()
    print(f"Growth directory: {growth_dir}")
    print()

    created = []
    for rel in REQUIRED_DIRS:
        full = os.path.join(growth_dir, rel)
        if not os.path.isdir(full):
            os.makedirs(full, exist_ok=True)
            created.append(rel)
            print(f"  Created: {rel}")
        else:
            print(f"  Exists:  {rel}")

    dashboard_path = os.path.join(growth_dir, "growth-dashboard.md")
    if not os.path.isfile(dashboard_path):
        os.makedirs(growth_dir, exist_ok=True)
        with open(dashboard_path, "w", encoding="utf-8") as fh:
            fh.write(DASHBOARD_TEMPLATE)
        print(f"\n  Created dashboard: {dashboard_path}")
    else:
        print(f"\n  Dashboard exists:  {dashboard_path}")

    print(f"\nCreated {len(created)} directories.")
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
