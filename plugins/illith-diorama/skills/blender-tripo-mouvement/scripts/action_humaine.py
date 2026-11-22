"""Capturer une prestation évaluée et en exporter une Action FK pour un humanoïde."""
import argparse
import gzip
import json
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


def arguments():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("mode", choices=["inventaire", "capture", "transfert"])
    cli.add_argument("--scene")
    cli.add_argument("--rig")
    cli.add_argument("--noms", type=Path, help="JSON : nom anatomique vers nom dans ce rig")
    cli.add_argument("--debut", type=int)
    cli.add_argument("--fin", type=int)
    cli.add_argument("--capture", type=Path, help="Prestation .json.gz")
    cli.add_argument("--sortie", type=Path, help="Nouvelle bibliothèque .blend")
    cli.add_argument("--nom", default="Mouvement transféré")
    return cli.parse_args(sys.argv[sys.argv.index("--") + 1:])


def orientations(points):
    up = (points["Head"] - points["Hips"]).normalized()
    across = points["LeftUpLeg"] - points["RightUpLeg"]
    right = (across - up * across.dot(up)).normalized()
    if right.length < .99 or up.length < .99:
        raise ValueError("Repères du bassin dégénérés")
    return Matrix((right, up.cross(right), up)).transposed().to_quaternion()


def legs(points):
    lengths = []
    for side in ("Left", "Right"):
        a, b, c = (points[side + suffix] for suffix in ("UpLeg", "Leg", "Foot"))
        lengths.append((a-b).length + (b-c).length)
    if min(lengths) < 1e-7:
        raise ValueError("Longueur de jambe nulle dans le squelette de repos")
    return sum(lengths) / 2


def names_for(rig, path):
    bones = rig.data.bones
    pairs = json.loads(path.read_text()) if path else {
        bone.name.rsplit(":", 1)[-1]: bone.name for bone in bones}
    if len(set(pairs.values())) != len(pairs) or (not path and len(pairs) != len(bones)):
        raise ValueError("Noms ambigus, fournir une correspondance bijective avec --noms")
    for name in ("Hips", "Head", "LeftUpLeg", "RightUpLeg", "LeftLeg", "RightLeg", "LeftFoot", "RightFoot"):
        if name not in pairs:
            raise ValueError("Ajouter au fichier --noms le repère " + name)
    for name in pairs.values():
        if bones.get(name) is None:
            raise ValueError("Os introuvable : " + name)
    return pairs


def uniform(matrix):
    scale = matrix.to_scale()
    if matrix.to_3x3().determinant() <= 0 or max(scale)-min(scale) > max(scale)*.001:
        raise ValueError("Uniformiser l’échelle du rig avant de transférer")
    return sum(scale) / 3


def capture(scene, rig, pairs, a):
    if a.debut is None or a.fin is None or a.fin <= a.debut or not a.capture:
        raise ValueError("Fournir --debut, --fin et --capture")
    scene.frame_set(a.debut)
    graph = bpy.context.evaluated_depsgraph_get()
    initial = rig.evaluated_get(graph).matrix_world.copy()
    initial_scale = uniform(initial)
    rest = {}
    for key, name in pairs.items():
        matrix = rig.data.bones[name].matrix_local
        rest[key] = [list(matrix.translation), list(matrix.to_quaternion())]
    frames = []
    for f in range(a.debut, a.fin + 1):
        scene.frame_set(f)
        ev = rig.evaluated_get(graph)
        if abs(uniform(ev.matrix_world) / initial_scale - 1) > .001:
            raise ValueError("Échelle du rig animée. Isoler la prestation hors de l’effet d’apparition.")
        relative = initial.inverted() @ ev.matrix_world
        matrices = [relative @ ev.pose.bones[name].matrix for name in pairs.values()]
        hips = matrices[list(pairs).index("Hips")].translation
        frames.append([list(hips), [list(m.to_quaternion().normalized()) for m in matrices]])
    data = dict(version=1, scene=scene.name, rig=rig.name, source_frames=[a.debut, a.fin],
                fps=scene.render.fps / scene.render.fps_base, rest=rest, keys=list(pairs), frames=frames)
    with gzip.open(a.capture, "xt", encoding="utf-8") as out:
        json.dump(data, out, separators=(",", ":"))
    print("Capture", len(frames), "poses,", len(pairs), "os,", a.capture)


def transfer(scene, rig, pairs, a):
    if not a.capture or not a.sortie or a.sortie.suffix != ".blend" or a.sortie.exists():
        raise ValueError("Préciser --capture et une nouvelle --sortie .blend")
    with gzip.open(a.capture, "rt", encoding="utf-8") as f:
        source = json.load(f)
    if source["version"] != 1:
        raise ValueError("Version inconnue")
    src = source["rest"]
    keys = [k for k in source["keys"] if k in pairs]
    target_names = {pairs[k]: k for k in keys}
    for bone in rig.pose.bones:
        if any(not c.mute and c.influence > 0 for c in bone.constraints):
            raise ValueError("Utiliser une copie FK sans contraintes actives, ou le transfert Rokoko")
        if not bone.bone.use_inherit_rotation:
            raise ValueError("Héritage de rotation spécial : utiliser un remappage dédié")
    positions = {k: rig.data.bones[pairs[k]].head_local.copy() for k in keys}
    reference = {k: Vector(src[k][0]) for k in keys}
    alignment = orientations(positions) @ orientations(reference).inverted()
    proportion = legs(positions) / legs(reference)
    rest_q = {b.name: b.matrix_local.to_quaternion() for b in rig.data.bones}
    source_inverse = {k: Quaternion(src[k][1]).inverted() for k in keys}
    order = sorted(rig.pose.bones, key=lambda b: len(b.parent_recursive))
    hips = rig.pose.bones[pairs["Hips"]]
    if hips.parent:
        raise ValueError("Le bassin doit être la racine FK ; adapter le contrôle maître séparément")
    # Only this in-memory rig is touched. The saved library contains the independent Action.
    rig.animation_data_clear()
    for bone in order:
        bone.matrix_basis = Matrix.Identity(4)
        bone.rotation_mode = "QUATERNION"
    action = bpy.data.actions.new(a.nom)
    rig.animation_data_create().action = action
    fps_ratio = (scene.render.fps / scene.render.fps_base) / source["fps"]
    start = a.debut if a.debut is not None else 1
    last = {}
    indices = {key: i for i, key in enumerate(source["keys"])}
    for i, (hip, rotations) in enumerate(source["frames"]):
        time = start + i * fps_ratio
        absolute = {}
        for bone in order:
            key = target_names.get(bone.name)
            parent_rot = absolute[bone.parent.name] if bone.parent else Quaternion()
            rest = rest_q[bone.name]
            bind = rest_q[bone.parent.name].inverted() @ rest if bone.parent else rest
            if key is None:
                absolute[bone.name] = parent_rot @ bind
                continue
            delta = Quaternion(rotations[indices[key]]) @ source_inverse[key]
            desired = alignment @ delta @ alignment.inverted() @ rest
            local = (bind.inverted() @ parent_rot.inverted() @ desired).normalized()
            if bone.name in last:
                local.make_compatible(last[bone.name])
            last[bone.name] = local.copy()
            absolute[bone.name] = desired
            bone.rotation_quaternion = local
            bone.keyframe_insert("rotation_quaternion", frame=time, group=bone.name)
        hip_offset = alignment @ (Vector(hip) - reference["Hips"]) * proportion
        hips.location = rest_q[hips.name].inverted() @ hip_offset
        hips.keyframe_insert("location", frame=time, group=hips.name)
    action.use_fake_user = True
    action["source_scene"] = source["scene"]
    action["source_rig"] = source["rig"]
    action["source_fps"] = source["fps"]
    action["target_fps"] = scene.render.fps / scene.render.fps_base
    action["os_transferes"] = len(keys)
    bpy.data.libraries.write(str(a.sortie.resolve()), {action}, fake_user=True, compress=True)
    print("Action", action.name, ":", len(keys), "os,", len(source["frames"]), "poses,", a.sortie)


a = arguments()
scene = bpy.data.scenes[a.scene] if a.scene else bpy.context.scene
bpy.context.window.scene = scene
if a.mode == "inventaire":
    for sc in bpy.data.scenes:
        print(sc.name, "  ", [o.name for o in sc.objects if o.type == "ARMATURE"])
else:
    rig = scene.objects.get(a.rig or "")
    if not rig or rig.type != "ARMATURE":
        raise ValueError("Choisir une armature de cette scène avec --rig")
    pairs = names_for(rig, a.noms)
    if a.mode == "capture":
        capture(scene, rig, pairs, a)
    else:
        transfer(scene, rig, pairs, a)
