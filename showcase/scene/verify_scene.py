"""Inventorier la scène du film depuis Blender. Le chemin JSON suit le séparateur --."""

from array import array
from hashlib import sha256
from pathlib import Path
import json
import sys

import bpy


def animation_digest():
    digest = sha256()
    curves = keys = 0
    for action in sorted(bpy.data.actions, key=lambda a: a.name):
        digest.update(action.name.encode())
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        curves += 1
                        keys += len(curve.keyframe_points)
                        digest.update(
                            f"{bag.slot_handle}:{curve.data_path}:{curve.array_index}".encode()
                        )
                        for field in ("co", "handle_left", "handle_right"):
                            values = array("f", [0]) * (2 * len(curve.keyframe_points))
                            curve.keyframe_points.foreach_get(field, values)
                            digest.update(values.tobytes())
    return dict(
        actions=len(bpy.data.actions),
        curves=curves,
        keys=keys,
        sha256=digest.hexdigest(),
    )


def main():
    scene = bpy.context.scene
    actors = sorted(
        (o for o in scene.objects if o.type == "ARMATURE"), key=lambda o: o.name
    )
    images = [i for i in bpy.data.images if i.source == "FILE"]
    assert all(i.packed_files and min(i.size) > 0 for i in images)
    assert not bpy.data.libraries
    poses = {}
    for frame in (185, 233, 905, 1453, 2186):
        scene.frame_set(frame)
        deps = bpy.context.evaluated_depsgraph_get()
        digest = sha256()
        for actor in actors:
            rig = actor.evaluated_get(deps)
            for bone in rig.pose.bones:
                for row in rig.matrix_world @ bone.matrix:
                    digest.update(
                        ",".join(str(round(x * 10000)) for x in row).encode() + b";"
                    )
        poses[frame] = digest.hexdigest()
    report = dict(
        scene=scene.name,
        blender=bpy.app.version_string,
        frames=[scene.frame_start, scene.frame_end],
        fps=scene.render.fps / scene.render.fps_base,
        camera=scene.camera.name,
        objects=len(scene.objects),
        packed_images=len(images),
        character_atlases={
            i.name: list(i.size) for i in images if "atlas4k-basecolor" in i.name
        },
        rigs={o.name: len(o.data.bones) for o in actors},
        poses=poses,
        animation=animation_digest(),
        markers={m.name: m.frame for m in scene.timeline_markers},
    )
    args = sys.argv[sys.argv.index("--") + 1 :]
    Path(args[0]).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(scene.name, report["packed_images"], report["animation"])


if __name__ == "__main__":
    main()
