from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):
    help = "Run the frontend build (yarn run build) if needed, then call collectstatic."

    def handle(self, *args: Any, **options: Any) -> None:
        yarn_path = shutil.which("yarn")
        if not yarn_path:
            raise CommandError("'yarn' not found in PATH; please install Node/yarn to build frontend assets")

        stats_path = Path(settings.BASE_DIR) / "webpack-stats.json"
        skip_build = False
        if stats_path.exists():
            try:
                with stats_path.open(encoding="utf-8") as fh:
                    stats = json.load(fh)
                assets = stats.get("assets", {}) or {}
                missing = []
                for asset in assets.values():
                    p = asset.get("path")
                    if not p or not Path(p).exists():
                        missing.append(p)
                if not missing:
                    skip_build = True
            except (json.JSONDecodeError, OSError):
                skip_build = False

        if skip_build:
            self.stdout.write(
                self.style.NOTICE("Skipping frontend build; assets present according to webpack-stats.json")
            )
        else:
            self.stdout.write(self.style.NOTICE("Running frontend build via yarn..."))
            try:
                subprocess.run([yarn_path, "run", "build"], check=True)  # noqa: S603
            except subprocess.CalledProcessError as exc:
                raise CommandError("Frontend build failed") from exc

        # Now run Django's collectstatic
        try:
            call_command("collectstatic", "--noinput")
        except CommandError as exc:  # pragma: no cover - fallback path
            raise CommandError("collectstatic failed") from exc
