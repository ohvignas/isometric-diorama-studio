"""Create the original, fully editable exercise scene in a fresh Blender process."""

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Quaternion

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "Atelier"
scene.render.engine = "CYCLES"
scene.cycles.samples = 12
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start, scene.frame_end = 1, 144
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.world = bpy.data.worlds.new("Ambiance")
scene.world.color = (0.32, 0.32, 0.32)


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = mat.diffuse_color
    node.inputs["Roughness"].default_value = 0.65
    return mat


oak = material("Chêne", (0.46, 0.22, 0.09))
cream = material("Chaux", (0.86, 0.76, 0.6))
green = material("Sauge", (0.22, 0.43, 0.35))
navy = material("Ardoise", (0.06, 0.10, 0.14))
coral = material("Terre cuite", (0.74, 0.27, 0.15))
skin = material("Hêtre", (0.76, 0.49, 0.28))


def box(name, center, size, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Chants arrondis", "BEVEL")
        mod.width, mod.segments = bevel, 3
        obj.modifiers.new("Normales", "WEIGHTED_NORMAL")
    return obj


def rise(obj, start, end):
    # The lower edge stays fixed while the wall gains height.
    obj["show_from"] = start
    z = obj.location.z
    half = obj.dimensions.z / 2
    for frame, fraction in [(start, 0.001), (end, 1.0)]:
        obj.scale.z = fraction
        obj.location.z = z - half * (1 - fraction)
        obj.keyframe_insert(data_path="scale", frame=frame)
        obj.keyframe_insert(data_path="location", frame=frame)


def sphere(name, center, radii, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = radii
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


rise(box("Socle", (0, 0, -0.11), (5.4, 4.4, 0.22), oak), 1, 14)
for i in range(12):
    rise(
        box(
            f"Lame {i+1:02}",
            (0, -2.01 + i * 0.365, 0.012),
            (5.32, 0.355, 0.024),
            oak,
            0.008,
        ),
        2 + i,
        14 + i,
    )
rise(box("Cloison gauche", (-2.63, 0, 1.25), (0.12, 4.32, 2.5), green), 10, 37)
rise(box("Cloison arrière", (0, 2.13, 1.25), (5.38, 0.12, 2.5), cream), 17, 42)
# Furniture stands on the floor throughout its assembly.
for x in (-0.81, 0.81):
    for y in (0.1, 0.8):
        rise(box("Pied du bureau", (x, y, 0.39), (0.065, 0.065, 0.74), navy), 28, 44)
rise(box("Plateau", (0, 0.45, 0.79), (1.83, 0.88, 0.085), oak), 39, 50)
for name, center, size, mat in [
    ("Pied écran", (0, 0.65, 0.91), (0.08, 0.09, 0.21), navy),
    ("Écran", (0, 0.66, 1.21), (0.81, 0.075, 0.47), navy),
    ("Dalle", (0, 0.615, 1.21), (0.75, 0.02, 0.40), green),
    ("Clavier", (0, 0.22, 0.86), (0.5, 0.18, 0.026), cream),
    ("Tapis", (-1.67, 0.25, 0.041), (1.31, 1.67, 0.026), green),
    ("Banc", (-1.8, 0.72, 0.46), (0.63, 1.11, 0.1), oak),
    ("Pied banc", (-1.8, 0.72, 0.25), (0.42, 0.72, 0.4), green),
]:
    rise(box(name, center, size, mat), 41, 56)
for i in range(7):
    box(
        "Livre",
        (-2.25, 0.15 + i * 0.10, 1.09),
        (0.29, 0.075, 0.30 + 0.03 * (i % 3)),
        [oak, coral, navy][i % 3],
        0.009,
    )
box("Tablette", (-2.38, 0.45, 0.9), (0.48, 1.06, 0.055), oak)
box("Bac", (1.95, 1.55, 0.26), (0.62, 0.62, 0.48), coral, 0.055)
for i in range(13):
    t = i * 2.4
    leaf = sphere(
        "Feuille",
        (1.95 + 0.17 * math.cos(t), 1.55 + 0.17 * math.sin(t), 0.65 + 0.025 * i),
        (0.09, 0.08, 0.27),
        green,
    )
    leaf.rotation_euler = (0.42 * math.sin(t), 0.42 * math.cos(t), t)

# An openly reusable demonstration rig. Geometry is attached to named bones.
origin = Vector((0.02, -0.32, 0.038))
arm = bpy.data.armatures.new("Anatomie FK")
rig = bpy.data.objects.new("Mannequin", arm)
scene.collection.objects.link(rig)
rig.location = origin
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
skeleton = {}


def bone(name, head, tail, parent=None):
    b = arm.edit_bones.new(name)
    b.head, b.tail = head, tail
    if parent:
        b.parent = arm.edit_bones[parent]
    skeleton[name] = (Vector(head), Vector(tail))


bone("Hips", (0, 0, 0.85), (0, 0, 1.03))
bone("Spine", (0, 0, 1.03), (0, 0, 1.42), "Hips")
bone("Head", (0, 0, 1.42), (0, 0, 1.69), "Spine")
for side, sign in (("Left", 1), ("Right", -1)):
    x = 0.14 * sign
    bone(side + "UpLeg", (x, 0, 0.86), (x, 0.02, 0.47), "Hips")
    bone(side + "Leg", (x, 0.02, 0.47), (x, -0.02, 0.11), side + "UpLeg")
    bone(side + "Foot", (x, -0.02, 0.11), (x, 0.17, 0.08), side + "Leg")
    bone(side + "Arm", (0.21 * sign, 0, 1.36), (0.27 * sign, 0.055, 1.11), "Spine")
    bone(
        side + "ForeArm",
        (0.27 * sign, 0.055, 1.11),
        (0.25 * sign, 0.29, 1.01),
        side + "Arm",
    )
    bone(
        side + "Hand",
        (0.25 * sign, 0.29, 1.01),
        (0.25 * sign, 0.41, 0.99),
        side + "ForeArm",
    )
bpy.ops.object.mode_set(mode="OBJECT")
for name, (head, tail) in skeleton.items():
    d = tail - head
    radius = 0.078 if "Leg" in name else 0.055
    if name in ("Spine", "Hips", "Head"):
        radius = {"Spine": 0.20, "Hips": 0.16, "Head": 0.135}[name]
    if name in ("Spine", "Hips"):
        size = (radius, radius * 0.66, d.length * 0.63)
    else:
        size = (radius, radius, d.length * 0.60)
    obj = sphere(
        name + " · volume",
        origin + (head + tail) / 2,
        size,
        (
            skin
            if name == "Head" or name.endswith("Hand")
            else green if name == "Spine" else navy
        ),
    )
    obj.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    bpy.context.view_layer.update()
    world = obj.matrix_world.copy()
    obj.parent = rig
    obj.parent_type = "BONE"
    obj.parent_bone = name
    obj.matrix_world = world
for f in range(1, 145):
    # Two hands alternate periodically during the last three seconds.
    phase = 2 * math.pi * (f - 73) / 24
    amount = min(1, max(0, (f - 48) / 24))
    for side, shift in (("Left", 0), ("Right", math.pi)):
        pb = rig.pose.bones[side + "ForeArm"]
        pb.rotation_quaternion = Quaternion(
            (1, 0, 0), amount * (0.12 + 0.14 * math.sin(phase + shift))
        )
        pb.keyframe_insert(data_path="rotation_quaternion", frame=f)
    pb = rig.pose.bones["Head"]
    pb.rotation_quaternion = Quaternion((0, 1, 0), 0.045 * amount * math.sin(phase / 3))
    pb.keyframe_insert(data_path="rotation_quaternion", frame=f)
rig.animation_data.action.name = "Clavier · mannequin"
for name, frame in (
    ("Construction", 1),
    ("Bureau", 28),
    ("Travail", 57),
    ("Boucle", 73),
):
    scene.timeline_markers.new(name, frame=frame)
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.225))
bpy.context.object.name = "Receveur ombre"
bpy.context.object.is_shadow_catcher = True
for name, place, power, size in [
    ("Fenêtre", (-3, -4, 7), 650, 5),
    ("Rebond", (4, 1, 5), 320, 4),
]:
    bpy.ops.object.light_add(type="AREA", location=place)
    light = bpy.context.object
    light.name = name
    light.data.energy, light.data.shape, light.data.size = power, "DISK", size
    light.rotation_euler = (-light.location).to_track_quat("-Z", "Y").to_euler()
bpy.ops.object.camera_add(location=(6.4, -8.4, 6))
camera = bpy.context.object
camera.name = "Plan fixe"
camera.rotation_euler = (
    (Vector((0, 0.05, 0.96)) - camera.location).to_track_quat("-Z", "Y").to_euler()
)
camera.data.type = "ORTHO"
camera.data.ortho_scale = 10.6
scene.camera = camera
for obj in scene.objects:
    if obj.type != "MESH" or obj.is_shadow_catcher:
        continue
    start = int(obj.get("show_from", 51 if obj.parent == rig else 47))
    if start > 1:
        for frame, hidden in ((1, True), (start - 1, True), (start, False)):
            obj.hide_render = hidden
            obj.keyframe_insert(data_path="hide_render", frame=frame)
scene.frame_set(96)
scene.render.filepath = "//render/"
dest = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
if dest.exists():
    raise FileExistsError(dest)
bpy.ops.wm.save_as_mainfile(filepath=str(dest), compress=True)
