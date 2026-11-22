"""Negotiate both real stdio servers and perform a cost-free read, using mcp 1.x."""

import asyncio
import json
import os
from pathlib import Path
import shutil
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1] / "plugins/isometric-diorama-studio"


async def check(name, config):
    exe = shutil.which(config["command"])
    if not exe:
        raise FileNotFoundError(config["command"])
    env = {"PATH": os.environ["PATH"], **config.get("env", {})}
    if name == "blender-lab" and shutil.which("blender"):
        env["BLENDER_PATH"] = shutil.which("blender")
    params = StdioServerParameters(command=exe, args=config["args"], env=env)
    async with stdio_client(params) as (src, dst):
        async with ClientSession(src, dst) as session:
            await session.initialize()
            tools = {tool.name: tool for tool in (await session.list_tools()).tools}
            if name == "blender-lab":
                key = "get_blendfile_summary_datablocks_for_cli"
                args = {"blend_file": str(ROOT / "examples/atelier.blend")}
            else:
                key = "tripo_usage"
                args = {}
            if key not in tools:
                raise ValueError(
                    f"{name} ne propose pas {key}. Outils présents : {sorted(tools)}"
                )
            result = await session.call_tool(key, args)
            if result.isError or not result.content:
                raise RuntimeError(f"Échec de la lecture {key}")
            if name == "blender-lab" and "Atelier" not in str(result.content):
                raise ValueError("Le serveur n'a pas retourné le contenu de l'atelier")
            print(f"{name}: {len(tools)} outils, lecture {key} réussie")


async def main():
    config = json.loads((ROOT / ".mcp.json").read_text())["mcpServers"]
    for name, server in config.items():
        await asyncio.wait_for(check(name, server), timeout=75)


if __name__ == "__main__":
    asyncio.run(main())
