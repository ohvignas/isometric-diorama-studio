"""Blender-side commands used by diorama.py. Run against an isolated scene."""

import json
from pathlib import Path
import sys
import bpy

args = json.loads(sys.argv[sys.argv.index("--") + 1])
scene = bpy.context.scene


def import_asset(path):
    suffix = Path(path).suffix.lower()
    before = set(bpy.data.objects)
    if suffix in (".gltf", ".glb"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif suffix == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    else:
        raise ValueError(f"Format attendu GLB, glTF ou FBX : {suffix}")
    objects = set(bpy.data.objects) - before
    if not objects:
        raise ValueError("Le fichier est vide")
    return objects


def report():
    images = []
    for image in bpy.data.images:
        if image.source not in ("FILE", "TILED", "SEQUENCE", "MOVIE"):
            continue
        images.append(
            dict(
                name=image.name,
                dimensions=list(image.size),
                packed=bool(image.packed_file),
                available=bool(image.packed_file)
                or Path(bpy.path.abspath(image.filepath)).is_file(),
            )
        )
    armatures = []
    for obj in scene.objects:
        if obj.type == "ARMATURE":
            armatures.append(
                dict(name=obj.name, bones=[b.name for b in obj.data.bones])
            )
    return dict(
        scene=scene.name,
        camera=scene.camera.name if scene.camera else None,
        fps=scene.render.fps / scene.render.fps_base,
        frames=[scene.frame_start, scene.frame_end],
        armatures=armatures,
        actions=[a.name for a in bpy.data.actions],
        images=images,
        meshes=sum(o.type == "MESH" for o in scene.objects),
        materials=len(bpy.data.materials),
    )


if args["op"] == "inspect":
    if args.get("asset"):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene = bpy.context.scene
        import_asset(args["asset"])
    with Path(args["report"]).open("x", encoding="utf8") as file:
        json.dump(report(), file, ensure_ascii=False, indent=2)
elif args["op"] == "import":
    actors = import_asset(args["asset"])
    root = bpy.data.objects.new(args["name"], None)
    scene.collection.objects.link(root)
    for obj in actors:
        if obj.parent is None:
            obj.parent = root
    root.location = args["position"]
    bpy.ops.file.pack_all()
    if Path(args["output"]).exists():
        raise FileExistsError(args["output"])
    bpy.ops.wm.save_as_mainfile(filepath=args["output"], compress=True)
elif args["op"] == "render":
    if not scene.camera:
        raise ValueError("Caméra de scène manquante")
    first = args["first"] if args["first"] is not None else scene.frame_start
    last = args["last"] if args["last"] is not None else scene.frame_end
    if not scene.frame_start <= first <= last <= scene.frame_end:
        raise ValueError("Intervalle hors de la scène")
    scene.frame_start, scene.frame_end = first, last
    scene.render.resolution_percentage = args["scale"]
    if scene.render.engine == "CYCLES":
        scene.cycles.samples = args["samples"]
    elif scene.render.engine == "BLENDER_EEVEE":
        scene.eevee.taa_render_samples = args["samples"]
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.use_border = False
    scene.render.use_file_extension = True
    scene.render.filepath = str(Path(args["frames"]) / "######")
    bpy.ops.render.render(animation=True)
