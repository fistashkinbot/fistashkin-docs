#!/usr/bin/env python3
"""
Генерирует docs/manifest.json — карту "путь_файла -> дата последнего коммита".

Запускается из корня репозитория (там, где лежит папка docs/).
Требует полную историю git (fetch-depth: 0 в actions/checkout),
иначе `git log` не найдёт коммиты для файлов.
"""

import json
import pathlib
import subprocess
import sys

DOCS_DIR = pathlib.Path("docs")
MANIFEST_PATH = DOCS_DIR / "manifest.json"
SKIP_NAMES = {"SUMMARY.md", "manifest.json"}


def last_commit_date(path: pathlib.Path) -> str | None:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cI", "--", str(path)],
        capture_output=True,
        text=True,
    )
    date = result.stdout.strip()
    return date or None


def main() -> int:
    if not DOCS_DIR.is_dir():
        print(f"Папка {DOCS_DIR} не найдена", file=sys.stderr)
        return 1

    manifest: dict[str, str] = {}

    for path in sorted(DOCS_DIR.rglob("*.md")):
        if path.name in SKIP_NAMES:
            continue

        rel = path.relative_to(DOCS_DIR).as_posix()
        date = last_commit_date(path)
        if date:
            manifest[rel] = date
        else:
            print(f"Не удалось получить дату коммита для {rel}", file=sys.stderr)

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Записано {len(manifest)} записей в {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
