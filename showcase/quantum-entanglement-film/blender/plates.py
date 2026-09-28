"""Background plates for the 2D-driven sequences (S05 tally, S07 no-signal), plus the
screen positions of the particles so the overlays line up with the 3D.
usage: python plates.py s04a|s04b|galaxy"""
import os, sys, json, math, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from qe_lib import *
from bpy_extras.object_utils import world_to_camera_view

which = sys.argv[1]
OUT = ROOT / "plates"
OUT.mkdir(exist_ok=True)


def project(sc, p):
    v = world_to_camera_view(sc, sc.camera, Vector(p))
    return [v.x * sc.render.resolution_x, (1 - v.y) * sc.render.resolution_y]


def edge_px(sc, center, radius):
    cam = sc.camera
    right = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
    a = project(sc, center)
    b = project(sc, Vector(center) + right * radius)
    return math.hypot(b[0] - a[0], b[1] - a[1])


if which in ("s04a", "s04b"):
    import s04_common as S
    sid, update = S.build("A" if which == "s04a" else "B")
    sc = bpy.context.scene
    t = (S.N - 1) / FPS
    sc.frame_set(S.N)
    update(t)
    orb = bpy.data.objects["P"]
    info = {"center": project(sc, orb.location), "radius_px": edge_px(sc, orb.location, 0.35)}
    # idle detector, no particle, no link
    for o in bpy.data.objects:
        if o.name.startswith(("P", "Link", "Burst", "Wave")) and o.type != "CAMERA":
            o.hide_render = True
    mat = bpy.data.materials["Det_pad"]
    for nd in mat.node_tree.nodes:
        if nd.bl_idname == "ShaderNodeEmission":
            nd.inputs["Color"].default_value = (0.35, 0.8, 1.0, 1)
            nd.inputs["Strength"].default_value = 1.2
    bpy.app.handlers.frame_change_pre.clear()
    sc.cycles.samples = 24
    sc.render.use_motion_blur = False
    sc.render.filepath = str(OUT / f"{which}_plate.png")
    bpy.ops.render.render(write_still=True)
    (OUT / f"{which}_plate.json").write_text(json.dumps(info))
    print("PLATE", which, info, flush=True)
    os._exit(0)
