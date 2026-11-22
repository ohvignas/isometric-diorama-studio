#!/usr/bin/env python3
"""Commandes locales de création et de livraison du diorama."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def binary(name):
    override = os.environ.get("BLENDER_PATH") if name == "blender" else None
    path = shutil.which(override or name)
    if not path and not override and name == "blender" and sys.platform == "darwin":
        candidate = Path("/Applications/Blender.app/Contents/MacOS/Blender")
        if candidate.is_file():
            path = str(candidate)
    if not path:
        raise ValueError(f"Commande introuvable : {override or name}")
    return path


def output_file(path):
    path = Path(path).resolve()
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


def existing(path):
    return str(Path(path).resolve(strict=True))


def blender(script, arguments, project=None):
    cmd = [binary("blender"), "-b", "--factory-startup", "-Y"]
    if project:
        cmd.append(existing(project))
    subprocess.run(
        cmd
        + ["-t", "3", "--python-exit-code", "5", "-P", str(script), "--", *arguments],
        check=True,
    )


def publish_dir(destination, build):
    dest = Path(destination).resolve()
    if dest.exists():
        raise FileExistsError(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
        staging = Path(tmp) / "output"
        staging.mkdir()
        build(staging)
        staging.rename(dest)


def encode(args, out):
    first, last = args.first, args.last
    total = last - first + 1
    if first < 0 or not 0 < args.loop_frames <= total or args.fps <= 0:
        raise ValueError("Plage, cadence ou durée de boucle incorrecte")
    frames = Path(args.frames).resolve(strict=True)
    for i in range(first, last + 1):
        if not (frames / f"{i:06d}.png").is_file():
            raise FileNotFoundError(frames / f"{i:06d}.png")
    for name, start, count in [
        ("film", first, total),
        ("boucle", last - args.loop_frames + 1, args.loop_frames),
    ]:
        src = [
            binary("ffmpeg"),
            "-v",
            "error",
            "-nostdin",
            "-n",
            "-framerate",
            str(args.fps),
            "-start_number",
            str(start),
            "-i",
            str(frames / "%06d.png"),
        ]
        rest = ["-an", "-frames:v", str(count), "-threads", "3"]
        # The actual RGB in transparent pixels must be composited before H.264.
        flat = (
            "[0:v]split[a][b];[a]drawbox=color="
            + args.background
            + ":t=fill:replace=1[bg];[bg][b]overlay=format=auto,format=yuv420p[v]"
        )
        jobs = [
            (
                "mp4",
                [
                    "-filter_complex_threads",
                    "2",
                    "-filter_complex",
                    flat,
                    "-map",
                    "[v]",
                    *rest,
                    "-c:v",
                    "libx264",
                    "-crf",
                    "19",
                    "-movflags",
                    "+faststart",
                ],
            ),
            (
                "webm",
                [
                    *rest,
                    "-vf",
                    "format=yuva420p",
                    "-c:v",
                    "libvpx-vp9",
                    "-row-mt",
                    "1",
                    "-cpu-used",
                    "5",
                    "-crf",
                    "30",
                    "-b:v",
                    "0",
                ],
            ),
        ]
        if args.apple:
            jobs.append(
                (
                    "alpha.mp4",
                    [
                        *rest,
                        "-vf",
                        "format=bgra",
                        "-c:v",
                        "hevc_videotoolbox",
                        "-alpha_quality",
                        ".95",
                        "-b:v",
                        "3M",
                        "-tag:v",
                        "hvc1",
                        "-movflags",
                        "+faststart",
                    ],
                )
            )
        for suffix, options in jobs:
            file = out / f"{name}.{suffix}"
            subprocess.run(src + options + [str(file)], check=True)
            streams = json.loads(
                subprocess.check_output(
                    [
                        binary("ffprobe"),
                        "-v",
                        "error",
                        "-select_streams",
                        "v:0",
                        "-count_packets",
                        "-show_streams",
                        "-of",
                        "json",
                        str(file),
                    ]
                )
            )["streams"]
            if len(streams) != 1 or int(streams[0]["nb_read_packets"]) != count:
                raise ValueError(f"Durée incorrecte : {file}")
            if (
                suffix == "webm"
                and str(
                    streams[0]
                    .get("tags", {})
                    .get("alpha_mode", streams[0].get("tags", {}).get("ALPHA_MODE"))
                )
                != "1"
            ):
                raise ValueError(f"Alpha absent : {file}")

    templates = ROOT / "templates"
    player = (templates / "hero.html").read_text(encoding="utf-8")
    probes = ["test-alpha.webm"]
    if args.apple:
        probes.append("test-alpha-hevc.mp4")
    else:
        player = player.replace('data-apple-alpha="true"', 'data-apple-alpha="false"')
    for probe in probes:
        shutil.copyfile(templates / probe, out / probe)
    poster = frames / f"{last:06d}.png"
    webp_encoder = shutil.which("cwebp")
    if webp_encoder:
        subprocess.run(
            [
                webp_encoder,
                "-quiet",
                "-q",
                "87",
                str(poster),
                "-o",
                str(out / "poster.webp"),
            ],
            check=True,
        )
    else:
        shutil.copyfile(poster, out / "poster.png")
        player = player.replace('poster="poster.webp"', 'poster="poster.png"')
    (out / "index.html").write_text(player, encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    cmds = p.add_subparsers(dest="op", required=True)
    cmds.add_parser("doctor", help="Repérer les dépendances locales, hors ligne")
    c = cmds.add_parser(
        "plan", help="Préparer un devis indicatif Tripo sans soumission"
    )
    c.add_argument("image")
    c.add_argument("--model", default="P2.0")
    c = cmds.add_parser("starter", help="Créer le bureau et son mannequin FK")
    c.add_argument("output")
    c = cmds.add_parser("inspect", help="Inventorier les rigs, images et Actions")
    c.add_argument("source")
    c.add_argument("--report", required=True)
    c = cmds.add_parser("import", help="Ajouter un modèle à une copie de scène")
    c.add_argument("project")
    c.add_argument("asset")
    c.add_argument("output")
    c.add_argument("--name", default="Personnage")
    c.add_argument("--position", type=float, nargs=3, default=(0, 0, 0))
    c = cmds.add_parser("render", help="Rendre une séquence de PNG RGBA")
    c.add_argument("project")
    c.add_argument("frames")
    c.add_argument("--first", type=int)
    c.add_argument("--last", type=int)
    c.add_argument("--scale", type=int, default=100)
    c.add_argument("--samples", type=int, default=16)
    c = cmds.add_parser("encode", help="Exporter un film et une boucle séparée")
    c.add_argument("frames")
    c.add_argument("output")
    for key in ["first", "last", "loop-frames", "fps"]:
        c.add_argument("--" + key, type=int, required=True)
    c.add_argument("--background", default="0xf4f1ec")
    c.add_argument(
        "--apple",
        action="store_true",
        help="Ajouter le HEVC alpha via VideoToolbox sur macOS",
    )
    a = p.parse_args()
    if a.op == "doctor":
        for name in (
            "blender",
            "blender-mcp",
            "tripo",
            "node",
            "ffmpeg",
            "ffprobe",
            "uv",
        ):
            try:
                print(name, binary(name))
            except ValueError:
                print(name, "absent")
    elif a.op == "plan":
        subprocess.run(
            [
                binary("tripo"),
                "make",
                existing(a.image),
                "--model",
                a.model,
                "--dry-run",
                "--json",
            ],
            check=True,
        )
    elif a.op == "starter":
        blender(ROOT / "templates/atelier.py", [output_file(a.output)])
    elif a.op == "inspect":
        source = existing(a.source)
        native = source.lower().endswith(".blend")
        request = dict(
            op=a.op, report=output_file(a.report), asset=None if native else source
        )
        blender(
            ROOT / "scripts/scene.py", [json.dumps(request)], source if native else None
        )
    elif a.op == "import":
        request = dict(
            op=a.op,
            asset=existing(a.asset),
            output=output_file(a.output),
            name=a.name,
            position=a.position,
        )
        blender(ROOT / "scripts/scene.py", [json.dumps(request)], a.project)
    elif a.op == "render":
        if not 1 <= a.scale <= 100 or a.samples < 1:
            p.error("échelle 1–100 et échantillons positifs requis")

        def render(out):
            request = dict(
                op=a.op,
                frames=str(out),
                first=a.first,
                last=a.last,
                scale=a.scale,
                samples=a.samples,
            )
            blender(ROOT / "scripts/scene.py", [json.dumps(request)], a.project)

        publish_dir(a.frames, render)
    elif a.op == "encode":
        if (
            len(a.background) != 8
            or not a.background.startswith("0x")
            or any(ch not in "0123456789abcdefABCDEF" for ch in a.background[2:])
        ):
            p.error("--background attend 0xRRGGBB")
        publish_dir(a.output, lambda out: encode(a, out))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(str(exc))
