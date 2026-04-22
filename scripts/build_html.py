"""
Render all Life OS HTML embeds from snapshots.json + Jinja2 templates into dist/.

Usage:
    python scripts/build_html.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS_PATH = REPO_ROOT / "data" / "snapshots.json"
TEMPLATES_DIR = REPO_ROOT / "templates"
DIST_DIR = REPO_ROOT / "dist"

# Mapping (template_name, out_name) — simple pages
SIMPLE_PAGES = [
    ("radar.html", "radar.html"),
    ("sankey_week.html", "sankey-week.html"),
    ("area_t2.html", "area-t2.html"),
    ("stacked_w16.html", "stacked-w16.html"),
    # pilier specific
    ("line_poids.html", "line-poids-interieur.html"),
    ("tree_family.html", "tree-family-famille.html"),
    ("sankey_revenu.html", "sankey-revenu-profi.html"),
    ("treemap_depenses.html", "treemap-depenses-profi.html"),
    ("skill_tree.html", "skill-tree-creation.html"),
    ("book_progression.html", "book-progression-spirituel.html"),
    ("line_predication.html", "line-predication-spirituel.html"),
]

# Parameterized (template, slug in output, pilier slug to pass in context)
PILIER_TEMPLATES = [
    "achievements_pilier.html",
    "sous_achievements_pilier.html",
    "sankey_pilier.html",
    "heatmap_habits.html",
    "tree_deps.html",
    "area_pilier.html",
    "gantt_pilier.html",
    "tasks_week_pilier.html",
    "journal_pilier.html",
]
PILIER_SLUGS = ["interieur", "famille", "pro_fi", "creation", "spirituel"]
ACCOUNT_TEMPLATES = ["treemap_transactions_account.html", "history_transactions_account.html"]
ACCOUNT_SLUGS = ["anthonny", "mirane"]


def main() -> None:
    snapshots = json.loads(SNAPSHOTS_PATH.read_text())
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # Attach helpers available in all templates
    env.globals["snap"] = snapshots

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    # Clear previous renders (but keep .nojekyll)
    for p in DIST_DIR.iterdir():
        if p.name == ".nojekyll":
            continue
        if p.is_file():
            p.unlink()
        else:
            shutil.rmtree(p)

    # .nojekyll so GitHub Pages serves underscores + dotfiles
    (DIST_DIR / ".nojekyll").write_text("")

    # Simple pages
    rendered = 0
    for tmpl_name, out_name in SIMPLE_PAGES:
        try:
            tmpl = env.get_template(tmpl_name)
        except Exception as e:  # noqa: BLE001
            print(f"  skip {tmpl_name} (not yet implemented): {e}")
            continue
        html = tmpl.render(snap=snapshots)
        (DIST_DIR / out_name).write_text(html)
        rendered += 1
        print(f"  rendered {out_name}")

    # Parameterized pilier pages
    for tmpl_name in PILIER_TEMPLATES:
        try:
            tmpl = env.get_template(tmpl_name)
        except Exception as e:  # noqa: BLE001
            print(f"  skip {tmpl_name} (not yet implemented): {e}")
            continue
        for slug in PILIER_SLUGS:
            pilier = snapshots["piliers"][slug]
            out_name = tmpl_name.replace(".html", f"-{slug}.html").replace("_", "-")
            html = tmpl.render(snap=snapshots, pilier=pilier, pilier_slug=slug)
            (DIST_DIR / out_name).write_text(html)
            rendered += 1
            print(f"  rendered {out_name}")

    # Parameterized account transaction pages
    for tmpl_name in ACCOUNT_TEMPLATES:
        try:
            tmpl = env.get_template(tmpl_name)
        except Exception as e:  # noqa: BLE001
            print(f"  skip {tmpl_name} (not yet implemented): {e}")
            continue
        for slug in ACCOUNT_SLUGS:
            account = snapshots.get("transactions_accounts", {}).get(slug)
            out_name = tmpl_name.replace(".html", f"-{slug}.html").replace("_", "-")
            html = tmpl.render(snap=snapshots, account=account, account_slug=slug)
            (DIST_DIR / out_name).write_text(html)
            rendered += 1
            print(f"  rendered {out_name}")

    # KPI embeds (one HTML per kpi_catalog entry)
    try:
        kpi_tmpl = env.get_template("kpi.html")
        for slug, kpi_data in snapshots.get("kpi_catalog", {}).items():
            out_name = f"kpi-{slug}.html"
            html = kpi_tmpl.render(snap=snapshots, kpi=kpi_data)
            (DIST_DIR / out_name).write_text(html)
            rendered += 1
            print(f"  rendered {out_name}")
    except Exception as e:
        print(f"  skip kpi rendering: {e}")

    # Index page listing all embeds for easy preview
    try:
        idx = env.get_template("_index.html")
        (DIST_DIR / "index.html").write_text(idx.render(snap=snapshots))
        rendered += 1
        print("  rendered index.html")
    except Exception as e:  # noqa: BLE001
        print(f"  skip index (not yet implemented): {e}")

    print(f"\nTotal rendered: {rendered} pages in {DIST_DIR}")


if __name__ == "__main__":
    main()
