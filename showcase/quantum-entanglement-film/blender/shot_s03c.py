"""S03c: 'Across the galaxy. The link between them does not fade.'"""
import os, sys, math, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from qe_lib import *

SHOT = "s03_apart"
info = shot_info(SHOT)
T0 = 4.3
T1 = info["frames"] / FPS
N = round((T1 - T0) * FPS)
sc = new_scene((1920, 1080), samples=10, frames=N, motion_blur=True)
world_sky(strength=0.22, rot_z=0.4, rot_x=1.2)

# the galaxy: emissive textured disc (texture is RGBA, alpha = coverage)
bpy.ops.mesh.primitive_plane_add(size=20)
gal = bpy.context.object
gm = bpy.data.materials.new("galaxy")
gm.use_nodes = True
G, GL = gm.node_tree.nodes, gm.node_tree.links
G.remove(G["Principled BSDF"])
tex = G.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(str(TEX / "galaxy.exr"))
tex.interpolation = "Cubic"
em = G.new("ShaderNodeEmission")
em.inputs["Strength"].default_value = 1.15
GL.new(tex.outputs["Color"], em.inputs["Color"])
tr = G.new("ShaderNodeBsdfTransparent")
mx = G.new("ShaderNodeMixShader")
# radial mask from UVs: the square plane must vanish outside the disc (texture alpha alone is not honoured)
uvn = G.new("ShaderNodeTexCoord")
sub = G.new("ShaderNodeVectorMath")
sub.operation = "SUBTRACT"
sub.inputs[1].default_value = (0.5, 0.5, 0.0)
GL.new(uvn.outputs["UV"], sub.inputs[0])
ln = G.new("ShaderNodeVectorMath")
ln.operation = "LENGTH"
GL.new(sub.outputs[0], ln.inputs[0])
rm = G.new("ShaderNodeMapRange")
rm.inputs[1].default_value = 0.40
rm.inputs[2].default_value = 0.49
rm.inputs[3].default_value = 1.0
rm.inputs[4].default_value = 0.0
GL.new(ln.outputs["Value"], rm.inputs[0])
am = G.new("ShaderNodeMath")
am.operation = "MULTIPLY"
GL.new(tex.outputs["Alpha"], am.inputs[0])
GL.new(rm.outputs[0], am.inputs[1])
GL.new(am.outputs[0], mx.inputs[0])
GL.new(tr.outputs[0], mx.inputs[1])
GL.new(em.outputs[0], mx.inputs[2])
GL.new(mx.outputs[0], G["Material Output"].inputs["Surface"])
gm.cycles.emission_sampling = "NONE"
assign(gal, gm)
gal.visible_shadow = False
gal.rotation_euler = (math.radians(62), 0, math.radians(18))
bulge = Burst("Bulge", (1.0, 0.82, 0.6))
bulge.obj.scale = (1.1, 1.1, 0.55)

M = gal.matrix_world.copy()


def on_disc(r, ang, lift=0.0):
    p = Vector((r * math.cos(ang), r * math.sin(ang), lift))
    return M @ p


A = Orb("A", radius=0.24, seed=0.0)
B = Orb("B", radius=0.24, seed=11.3)
link_ = Link("Link", n=420, radius=0.012, strength=1.6)
cam = camera((0, -27, 6.5), (0, 0, 0), lens=42)
t_link = word_time(SHOT, "link")
TG0 = info["start"] / FPS
angA, angB = math.radians(205), math.radians(20)


def update(t):
    tl = t - T0
    tg = TG0 + t
    gal.rotation_euler = (math.radians(62), 0, math.radians(18) + 0.012 * tl)
    Mw = Euler((math.radians(62), 0, math.radians(18) + 0.012 * tl)).to_matrix().to_4x4()
    bulge.set(Vector((0, 0, 0)), 1.0, 2.2)
    bulge.obj.scale = (1.3, 1.3, 0.6)
    bulge.obj.rotation_euler = gal.rotation_euler
    f = ease_out_expo(clamp((tl - 0.05) / 1.0))
    pa = Mw @ Vector((6.2 * math.cos(angA), 6.2 * math.sin(angA), 0.25))

    def path(s_):
        ang = lerp(angA, angA - (angA - angB) * f, s_)
        r = 6.2 - 2.2 * math.sin(math.pi * s_) * f
        return Mw @ Vector((r * math.cos(ang), r * math.sin(ang), 0.25 + 1.6 * math.sin(math.pi * s_) * f))
    A.obj.location = pa
    B.obj.location = path(1.0)
    pulse = math.exp(-((t - (t_link + 0.35)) / 0.6) ** 2)
    A.set(tg, energy=1.8 + 1.5 * pulse)
    B.set(tg, energy=1.8 + 1.5 * pulse)
    link_.update_curve(path, tg, amp=0.05, turns=70 * max(f, 0.05), strength=1.6 + 2.8 * pulse)
    k = smoother(tl / (T1 - T0))
    cam.location = Vector((lerp(-1.0, 2.0, k), lerp(-26.0, -30.5, k), lerp(6.0, 8.0, k)))
    aim(cam, Vector((0, 0, lerp(0.3, 0.0, k))))


if os.environ.get("QE_PLATE"):
    import json
    from bpy_extras.object_utils import world_to_camera_view
    tl_end = T1 - 1 / FPS
    sc.frame_set(N)
    update(tl_end)
    pr = lambda p: [world_to_camera_view(sc, cam, p).x * 1920, (1 - world_to_camera_view(sc, cam, p).y) * 1080]
    info = {"A": pr(A.obj.location), "B": pr(B.obj.location), "center": pr(Vector((0, 0, 0)))}
    for o in bpy.data.objects:
        if o.name.startswith(("A", "B", "Link")) and o.name != "Bulge":
            o.hide_render = True
    bpy.app.handlers.frame_change_pre.clear()
    sc.cycles.samples = 24
    sc.render.use_motion_blur = False
    out = ROOT / "plates"
    out.mkdir(exist_ok=True)
    sc.render.filepath = str(out / "galaxy_plate.png")
    bpy.ops.render.render(write_still=True)
    (out / "galaxy_plate.json").write_text(json.dumps(info))
    print("PLATE galaxy", info, flush=True)
    os._exit(0)
run("s03c", update, time_map=lambda f: T0 + (f - 1) / FPS)
