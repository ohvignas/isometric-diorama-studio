"""Check what a fresh clone can load, using only the standard library."""

from pathlib import Path
import json
import re
from urllib.parse import unquote

repo = Path(__file__).resolve().parents[1]
plugin = repo / "plugins/isometric-diorama-studio"


def load(path):
    return json.loads(path.read_text(encoding="utf8"))


name = plugin.name
for f in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
    manifest = load(plugin / f)
    assert manifest["name"] == name and manifest["version"] == "1.1.0"
for f in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
    item = load(repo / f)["plugins"][0]
    src = item["source"]
    path = src["path"] if isinstance(src, dict) else src
    assert (repo / path).resolve() == plugin and item["name"] == name
servers = load(plugin / ".mcp.json")["mcpServers"]
assert servers == load(plugin / "mcp.json")["mcpServers"]
assert {s["command"] for s in servers.values()} == {"tripo", "blender-mcp"}
skills = list((plugin / "skills").glob("*/SKILL.md"))
assert len(skills) == 6
for skill in skills:
    header = skill.read_text().split("---", 2)[1]
    assert "name: " + skill.parent.name + "\n" in header and "\ndescription: " in header
for page in repo.rglob("*.md"):
    for dest in re.findall(r"\]\(([^)\n]+)\)", page.read_text()):
        if not dest.startswith(("https://", "http://", "#")):
            assert (page.parent / unquote(dest.split("#", 1)[0])).exists(), (page, dest)
for file in [
    "scripts/scene.py",
    "scripts/diorama.py",
    "templates/atelier.py",
    "templates/hero.html",
    "examples/reef-fish.glb",
    "examples/atelier.blend",
    "agents/regie-animation.md",
]:
    assert (plugin / file).is_file(), file
print("Catalogues, manifestes, 2 MCP, 6 skills et liens locaux vérifiés.")
