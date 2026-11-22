"""Vérifier les rotations et la trajectoire reconstruites sur le rig donneur."""
import argparse
import gzip
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Quaternion, Vector


cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--capture", type=Path, required=True)
cli.add_argument("--bibliotheque", type=Path, required=True)
cli.add_argument("--action", required=True)
cli.add_argument("--noms", type=Path)
cli.add_argument("--premiere-cle", type=int, default=1)
cli.add_argument("--tolerance-deg", type=float, default=.1)
cli.add_argument("--tolerance-mm", type=float, default=.1)
cli.add_argument("--rapport", type=Path, required=True)
args = cli.parse_args(sys.argv[sys.argv.index("--") + 1:])
with gzip.open(args.capture, "rt", encoding="utf-8") as stream:
    capture = json.load(stream)
scene = bpy.data.scenes[capture["scene"]]
bpy.context.window.scene = scene
scene.frame_set(capture["source_frames"][0])
rig = scene.objects[capture["rig"]]
names = json.loads(args.noms.read_text()) if args.noms else {
    b.name.rsplit(":", 1)[-1]: b.name for b in rig.pose.bones}
with bpy.data.libraries.load(str(args.bibliotheque.resolve())) as (src, dst):
    if args.action not in src.actions:
        raise ValueError("Action introuvable dans la bibliothèque")
    dst.actions = [args.action]
world = rig.matrix_world.copy()
rig.animation_data_clear()
rig.parent = None
rig.matrix_world = world
for bone in rig.pose.bones:
    bone.matrix_basis = Matrix.Identity(4)
    bone.rotation_mode = "QUATERNION"
rig.animation_data_create().action = dst.actions[0]
ratio = (scene.render.fps / scene.render.fps_base) / capture["fps"]
unit = scene.unit_settings.scale_length
graph = bpy.context.evaluated_depsgraph_get()
angle_max, dist_max = 0., 0.
for i, (position, rotations) in enumerate(capture["frames"]):
    time = args.premiere_cle + i * ratio
    scene.frame_set(math.floor(time), subframe=time % 1)
    ev = rig.evaluated_get(graph)
    for name, expected in zip(capture["keys"], rotations):
        rotation = ev.pose.bones[names[name]].matrix.to_quaternion()
        delta = Quaternion(expected).inverted() @ rotation
        magnitude = math.hypot(delta.x, delta.y, delta.z)
        angle_max = max(angle_max, math.degrees(2 * math.atan2(magnitude, abs(delta.w))))
    delta_p = ev.pose.bones[names["Hips"]].head - Vector(position)
    dist_max = max(dist_max, (world.to_3x3() @ delta_p).length * 1000 * unit)
result = {"poses": len(capture["frames"]), "os": len(capture["keys"]),
          "ecart_rotation_max_deg": angle_max, "ecart_bassin_max_mm": dist_max}
with args.rapport.open("x", encoding="utf-8") as out:
    json.dump(result, out, ensure_ascii=False, indent=2)
print(result)
if angle_max > args.tolerance_deg or dist_max > args.tolerance_mm:
    raise ValueError("La reconstruction s’écarte de la prestation. Voir le rapport.")
