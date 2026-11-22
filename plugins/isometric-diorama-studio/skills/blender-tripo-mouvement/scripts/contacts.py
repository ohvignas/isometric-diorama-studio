"""Mesurer dans un .blend les déplacements des accessoires et des semelles déformées."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np


def stationary(obj, frames, scene, graph, metres):
    origins, rotations = [], []
    for f in frames:
        scene.frame_set(f)
        world = obj.evaluated_get(graph).matrix_world
        origins.append(np.array(world.translation) * metres)
        rotations.append(world.to_quaternion().normalized())
    positions = np.array(origins)
    angles = []
    for rotation in rotations:
        relative = rotations[0].inverted() @ rotation
        vector_length = math.hypot(relative.x, relative.y, relative.z)
        angles.append(math.degrees(2 * math.atan2(vector_length, abs(relative.w))))
    distances = np.linalg.norm(positions - positions[0], axis=1)
    return {"excursion_mm": float(distances.max() * 1000),
            "cumul_mm": float(np.linalg.norm(np.diff(positions, axis=0), axis=1).sum()*1000),
            "rotation_deg": max(angles), "image_excursion": frames[int(distances.argmax())]}


def selection(scene, check):
    rig = scene.objects[check["rig"]]
    names = set(check["groupes"])
    parts = []
    for obj in scene.objects:
        if obj.type != "MESH" or obj.find_armature() != rig:
            continue
        groups = {g.index for g in obj.vertex_groups if g.name in names}
        ids = [v.index for v in obj.data.vertices if
               sum(w.weight for w in v.groups if w.group in groups) >= check.get("poids_min", .48)]
        if ids:
            parts.append((obj, ids))
    if not parts:
        raise ValueError("Aucun sommet pondéré pour " + str(names))
    return parts


def shoe(scene, graph, check, frames, metres):
    parts = selection(scene, check)
    floor = check["sol_m"]
    band = check.get("bande_contact_mm", 6.) / 1000
    prior = None
    slips, minima, runs = [], [], []
    run = 0.
    for f in frames:
        scene.frame_set(f)
        vertices = []
        for obj, indices in parts:
            ev = obj.evaluated_get(graph)
            if len(ev.data.vertices) != len(obj.data.vertices):
                raise ValueError("Stabiliser la topologie évaluée pour suivre les mêmes sommets")
            co = np.empty(len(ev.data.vertices)*3, dtype="f")
            ev.data.vertices.foreach_get("co", co)
            matrix = np.asarray(ev.matrix_world)
            vertices.append((co.reshape(-1, 3)[indices] @ matrix[:3,:3].T + matrix[:3,3]) * metres)
        current = np.vstack(vertices)
        minima.append(float(current[:,2].min()-floor))
        if prior is not None:
            valid = (current[:,2] <= floor + band) & (prior[:,2] <= floor + band)
            if np.any(valid):
                individual = np.linalg.norm(current[valid,:2] - prior[valid,:2], axis=1)
                # Opposing directions during a planted pivot must not cancel.
                step = float(np.median(individual))
                slips.append(step)
                run += step
            elif run:
                runs.append(run)
                run = 0.
        prior = current
    if not slips:
        raise ValueError("Aucun intervalle avec point de semelle en appui ; vérifier sol, groupes et dates")
    return {"appuis_mesures": len(slips), "glisse_mediane_mm": float(np.median(slips)*1000),
            "glisse_max_image_mm": max(slips)*1000, "glisse_cumulee_max_appui_mm": max([run]+runs)*1000,
            "penetration_mm": max(0., -min(minima))*1000,
            "hauteur_max_semelle_mm": max(minima)*1000}


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--config", type=Path, required=True)
parser.add_argument("--rapport", type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
cfg = json.loads(args.config.read_text())
scene = bpy.data.scenes[cfg["scene"]] if "scene" in cfg else bpy.context.scene
bpy.context.window.scene = scene
graph = bpy.context.evaluated_depsgraph_get()
metres = float(cfg.get("metres_par_unite", scene.unit_settings.scale_length))
if not cfg["controles"] or metres <= 0:
    raise ValueError("Spécifier un contrôle et une échelle positive")
report = []
for check in cfg["controles"]:
    frames = list(range(check["debut"], check["fin"]+1))
    if len(frames) < 2:
        raise ValueError("Préciser au moins deux images")
    if check["type"] == "objet_fixe":
        measured = stationary(scene.objects[check["objet"]], frames, scene, graph, metres)
    elif check["type"] == "semelle":
        measured = shoe(scene, graph, check, frames, metres)
    else:
        raise ValueError("Type de contrôle inconnu")
    errors = [key for key, limit in check.get("limites", {}).items() if measured[key] > limit]
    report.append(dict(nom=check["nom"], images=[frames[0],frames[-1]], mesures=measured, hors_limites=errors))
with args.rapport.open("x", encoding="utf-8") as out:
    json.dump(report, out, ensure_ascii=False, indent=2)
print(json.dumps(report, ensure_ascii=False))
if any(row["hors_limites"] for row in report):
    raise ValueError("Un contrôle dépasse la tolérance indiquée. Voir " + str(args.rapport))
