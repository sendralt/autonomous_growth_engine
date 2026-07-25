from __future__ import annotations

import os
from typing import Any

from flask import Request, Response

from helpers.api import ApiHandler, Input, Output
from helpers.plugins import get_plugin_config

from usr.plugins.autonomous_growth_engine.helpers import growth_io

PLUGIN_NAME = "autonomous_growth_engine"


class Dashboard(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        action = str(input.get("action", "") or "").strip().lower()
        context_id = str(input.get("context_id", "") or "").strip()

        try:
            if action == "stats":
                return self._stats(context_id)
            if action == "review_queue":
                return self._review_queue(context_id, input)
            if action == "read_file":
                return self._read_file(input)
            if action == "approve":
                return self._approve(context_id, input)
            if action == "reject":
                return self._reject(input)
            if action == "publish":
                return self._publish(context_id, input)
            if action == "update_metrics":
                return self._update_metrics(context_id, input)
        except FileNotFoundError as exc:
            return Response(status=404, response=str(exc))
        except ValueError as exc:
            return Response(status=400, response=str(exc))

        return Response(status=400, response=f"Unknown action: {action}")

    def _config(self, context_id: str) -> dict[str, Any]:
        return get_plugin_config(PLUGIN_NAME) or {}

    def _growth_dir(self, context_id: str) -> str:
        return growth_io.get_growth_dir(self._config(context_id), context_id)

    def _stats(self, context_id: str) -> dict[str, Any]:
        growth_dir = self._growth_dir(context_id)
        review_items = growth_io.list_review_items(growth_dir)
        pipeline_items = growth_io.list_pipeline_items(growth_dir)
        published_items = growth_io.list_published_items(growth_dir)
        research_items = growth_io.list_research_items(growth_dir)
        dashboard = growth_io.parse_dashboard(growth_dir)

        review_by_type: dict[str, int] = {}
        for item in review_items:
            rtype = item.get("type", "unknown")
            review_by_type[rtype] = review_by_type.get(rtype, 0) + 1

        return {
            "ok": True,
            "growth_dir": growth_dir,
            "counts": {
                "research": len(research_items),
                "review": len(review_items),
                "pipeline": len(pipeline_items),
                "published": len(published_items),
            },
            "review_by_type": review_by_type,
            "research_by_type": self._group_by_type(research_items),
            "dashboard": {
                "exists": dashboard.get("exists", False),
                "path": dashboard.get("path", ""),
                "sections": dashboard.get("sections", {}),
            },
        }

    def _group_by_type(self, items: list[dict[str, Any]]) -> dict[str, int]:
        result: dict[str, int] = {}
        for item in items:
            rtype = item.get("type", "unknown")
            result[rtype] = result.get(rtype, 0) + 1
        return result

    def _review_queue(self, context_id: str, input: Input) -> dict[str, Any]:
        growth_dir = self._growth_dir(context_id)
        content_filter = str(input.get("filter", "") or "").strip().lower()
        items = growth_io.list_review_items(growth_dir)
        if content_filter and content_filter != "all":
            items = [i for i in items if i.get("type") == content_filter]
        return {"ok": True, "items": items}

    def _read_file(self, input: Input) -> dict[str, Any]:
        path = str(input.get("source_path", "") or "").strip()
        if not path:
            raise ValueError("source_path is required")
        content = growth_io.read_text_file(path)
        return {"ok": True, "path": path, "content": content}

    def _approve(self, context_id: str, input: Input) -> dict[str, Any]:
        source_path = str(input.get("source_path", "") or "").strip()
        if not source_path:
            raise ValueError("source_path is required")
        dest_dir = os.path.join(self._growth_dir(context_id), "pipeline")
        new_path = growth_io.move_file(source_path, dest_dir)
        return {"ok": True, "source_path": source_path, "new_path": new_path}

    def _reject(self, input: Input) -> dict[str, Any]:
        source_path = str(input.get("source_path", "") or "").strip()
        if not source_path:
            raise ValueError("source_path is required")
        growth_io.delete_file(source_path)
        return {"ok": True, "deleted": source_path}

    def _publish(self, context_id: str, input: Input) -> dict[str, Any]:
        source_path = str(input.get("source_path", "") or "").strip()
        if not source_path:
            raise ValueError("source_path is required")
        dest_dir = os.path.join(self._growth_dir(context_id), "published")
        new_path = growth_io.move_file(source_path, dest_dir)
        return {"ok": True, "source_path": source_path, "new_path": new_path}

    def _update_metrics(self, context_id: str, input: Input) -> dict[str, Any]:
        section = str(input.get("section", "") or "").strip()
        content = str(input.get("content", "") or "")
        if not section:
            raise ValueError("section is required")
        growth_dir = self._growth_dir(context_id)
        path = growth_io.update_dashboard_section(growth_dir, section, content)
        growth_io.touch_dashboard(growth_dir)
        return {"ok": True, "path": path}
