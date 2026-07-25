from __future__ import annotations

import os
from typing import Any

from flask import Request, Response

from helpers.api import ApiHandler, Input, Output
from helpers.plugins import get_plugin_config

from usr.plugins.autonomous_growth_engine.helpers import growth_io

PLUGIN_NAME = "autonomous_growth_engine"

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


class Setup(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        action = str(input.get("action", "") or "").strip().lower()
        context_id = str(input.get("context_id", "") or "").strip()

        try:
            if action == "status":
                return self._status(context_id)
            if action == "initialize":
                return self._initialize(context_id)
        except ValueError as exc:
            return Response(status=400, response=str(exc))

        return Response(status=400, response=f"Unknown action: {action}")

    def _config(self, context_id: str) -> dict[str, Any]:
        return get_plugin_config(PLUGIN_NAME) or {}

    def _growth_dir(self, context_id: str) -> str:
        return growth_io.get_growth_dir(self._config(context_id), context_id)

    def _status(self, context_id: str) -> dict[str, Any]:
        growth_dir = self._growth_dir(context_id)
        dirs = growth_io.full_directory_structure()
        existing: list[str] = []
        missing: list[str] = []
        for rel in dirs:
            full = os.path.join(growth_dir, rel)
            if os.path.isdir(full):
                existing.append(rel)
            else:
                missing.append(rel)
        dashboard_exists = os.path.isfile(growth_io.dashboard_path(growth_dir))
        fully_initialized = len(missing) == 0 and dashboard_exists
        return {
            "ok": True,
            "growth_dir": growth_dir,
            "directories": {"existing": existing, "missing": missing},
            "dashboard_exists": dashboard_exists,
            "initialized": fully_initialized,
        }

    def _initialize(self, context_id: str) -> dict[str, Any]:
        growth_dir = self._growth_dir(context_id)
        created_dirs: list[str] = []
        for rel in growth_io.full_directory_structure():
            full = os.path.join(growth_dir, rel)
            growth_io.ensure_directory(full)
            created_dirs.append(rel)

        dashboard = growth_io.dashboard_path(growth_dir)
        if not os.path.isfile(dashboard):
            growth_io.ensure_directory(growth_dir)
            with open(dashboard, "w", encoding="utf-8") as fh:
                fh.write(DASHBOARD_TEMPLATE)

        return {
            "ok": True,
            "growth_dir": growth_dir,
            "created_directories": created_dirs,
            "dashboard_path": dashboard,
            "message": "Growth engine directory structure initialized.",
        }
