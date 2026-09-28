"""S06: hidden balls in boxes (colours fixed from the start) versus entangled particles (no hidden answer)."""
import sys, math, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from qe_lib import *

SID = "s06_boxes"
info = shot_info(SID)
N = info["frames"]
RES = (1280, 720)
sc = new_scene(RES, samples=8, frames=N, denoise=True, motion_blur=False)
sc.cycles.diffuse_bounces = 2
sc.cycles.glossy_bounces = 2
world_hdri(TEX / "studio.hdr", strength=0.55, rot_z=1.1, background_color=(0.0035, 0.004, 0.006))

# floor
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
floor = bpy.context.object
fm = principled("floor", (0.018, 0.019, 0.022), 0.0, 0.62)
assign(floor, fm)

area_light("Key", (-3.5, -3.2, 4.2), (0, 0, 0.4), size=3.0, power=520, color=(1.0, 0.95, 0.9))
area_light("Rim", (3.8, 3.0, 2.6), (0, 0, 0.5), size=2.0, power=420, color=(0.7, 0.82, 1.0))
area_light("Fill", (2.5, -4.5, 1.2), (0, 0, 0.4), size=4.0, power=90, color=(0.9, 0.92, 1.0))


def xray_box(name, x):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0.36))
    box = bpy.context.object
    box.name = name
    box.scale = (0.82, 0.82, 0.72)
    bpy.ops.object.transform_apply(scale=True)
    bev = box.modifiers.new("bevel", "BEVEL")
    bev.width = 0.05
    bev.segments = 5
    bev.limit_method = "ANGLE"
    for p in box.data.polygons:
        p.use_smooth = True
    box.data.shade_smooth()
    m = bpy.data.materials.new(name + "_mat")
    m.use_nodes = True
    nt = m.node_tree
    Nn, L = nt.nodes, nt.links
    metal = Nn["Principled BSDF"]
    metal.inputs["Base Color"].default_value = (0.62, 0.63, 0.66, 1)
    metal.inputs["Metallic"].default_value = 1.0
    metal.inputs["Roughness"].default_value = 0.3
    metal.inputs["Anisotropic"].default_value = 0.5
    xr = Nn.new("ShaderNodeValue")
    xr.name = "xr"
    lw = Nn.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    edge = Nn.new("ShaderNodeMath")
    edge.operation = "POWER"
    edge.inputs[1].default_value = 2.0
    L.new(lw.outputs["Facing"], edge.inputs[0])
    tc = Nn.new("ShaderNodeTexCoord")
    wave = Nn.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = 2.2
    ph = Nn.new("ShaderNodeValue")
    ph.name = "phase"
    L.new(tc.outputs["Object"], wave.inputs["Vector"])
    L.new(ph.outputs[0], wave.inputs["Phase Offset"])
    sharp = Nn.new("ShaderNodeMapRange")
    sharp.inputs[1].default_value = 0.85
    sharp.inputs[2].default_value = 1.0
    L.new(wave.outputs["Fac"], sharp.inputs[0])
    sum_ = Nn.new("ShaderNodeMath")
    sum_.operation = "MULTIPLY_ADD"
    sum_.inputs[1].default_value = 0.35
    L.new(sharp.outputs[0], sum_.inputs[0])
    L.new(edge.outputs[0], sum_.inputs[2])
    k = Nn.new("ShaderNodeMath")
    k.operation = "MULTIPLY"
    k.inputs[1].default_value = 2.2
    L.new(sum_.outputs[0], k.inputs[0])
    em = Nn.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.35, 0.8, 1.0, 1)
    L.new(k.outputs[0], em.inputs["Strength"])
    tr = Nn.new("ShaderNodeBsdfTransparent")
    add = Nn.new("ShaderNodeAddShader")
    L.new(tr.outputs[0], add.inputs[0])
    L.new(em.outputs[0], add.inputs[1])
    mix = Nn.new("ShaderNodeMixShader")
    L.new(xr.outputs[0], mix.inputs[0])
    L.new(metal.outputs[0], mix.inputs[1])
    L.new(add.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], Nn["Material Output"].inputs["Surface"])
    m.cycles.emission_sampling = "NONE"
    assign(box, m)
    # lid seam and a status light
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0.56))
    seam = bpy.context.object
    seam.scale = (0.835, 0.835, 0.012)
    sm = bpy.data.materials.new(name + "_seam")
    sm.use_nodes = True
    snt = sm.node_tree
    sb = snt.nodes["Principled BSDF"]
    sb.inputs["Base Color"].default_value = (0.01, 0.01, 0.012, 1)
    sb.inputs["Roughness"].default_value = 0.5
    sxr = snt.nodes.new("ShaderNodeValue")
    sxr.name = "xr"
    stc = snt.nodes.new("ShaderNodeBsdfTransparent")
    smx = snt.nodes.new("ShaderNodeMixShader")
    snt.links.new(sxr.outputs[0], smx.inputs[0])
    snt.links.new(sb.outputs[0], smx.inputs[1])
    snt.links.new(stc.outputs[0], smx.inputs[2])
    snt.links.new(smx.outputs[0], snt.nodes["Material Output"].inputs["Surface"])
    assign(seam, sm)
    return box, m, sm


boxL, mL, sL = xray_box("BoxL", -1.25)
boxR, mR, sR = xray_box("BoxR", 1.25)
# transform_apply bakes location into the mesh, so mark the box centres for screen tracking
empty("BoxLc", (-1.25, 0, 0.36))
empty("BoxRc", (1.25, 0, 0.36))
ballL = uv_sphere("BallL", 0.22, 64, 32, (-1.25, 0, 0.36))
assign(ballL, principled("ballBlue", (0.03, 0.18, 0.75), 0.0, 0.22, **{"Coat Weight": 0.6}))
ballR = uv_sphere("BallR", 0.22, 64, 32, (1.25, 0, 0.36))
assign(ballR, principled("ballGold", (0.85, 0.48, 0.05), 0.0, 0.22, **{"Coat Weight": 0.6}))
oL = Orb("OL", (-1.25, 0, 0.36), radius=0.24, seed=2.0)
oR = Orb("OR", (1.25, 0, 0.36), radius=0.24, seed=9.0)
oL.light_power = oR.light_power = 6.0
link_ = Link("Link", n=360, radius=0.0022, strength=1.4)
burstL = Burst("BurstL")
burstR = Burst("BurstR")
focus = empty("Focus", (0, 0, 0.35))
cam = camera((0.3, -5.6, 1.7), (0, 0, 0.35), lens=50)

w = lambda word, n=0: word_time(SID, word, n)
t_blue, t_gold, t_no = w("blue"), w("gold"), w("no")
t_ent = w("entangled")
t_that = w("that", 1)
TG0 = info["start"] / FPS


def set_xr(mat, seam, v, phase):
    mat.node_tree.nodes["xr"].outputs[0].default_value = v
    mat.node_tree.nodes["phase"].outputs[0].default_value = phase
    seam.node_tree.nodes["xr"].outputs[0].default_value = v


def update(t):
    tg = TG0 + t
    xl = smoother((t - (t_blue - 0.1)) / 0.45)
    xrr = smoother((t - (t_gold - 0.1)) / 0.45)
    set_xr(mL, sL, xl, t * 3.0)
    set_xr(mR, sR, xrr, t * 3.0 + 1.3)
    # balls become entangled particles
    m = smoother((t - (t_ent - 0.2)) / 0.6)
    s_ball = 1 - m
    ballL.scale = ballR.scale = (max(s_ball, 1e-3),) * 3
    set_visible(ballL, s_ball > 0.01)
    set_visible(ballR, s_ball > 0.01)
    oL.set_scale(max(m, 1e-3))
    oR.set_scale(max(m, 1e-3))
    set_visible(oL.obj, m > 0.01)
    set_visible(oR.obj, m > 0.01)
    fl = math.exp(-max(t - t_ent, 0) / 0.25) if t >= t_ent - 0.2 else 0.0
    oL.set(tg, flash=0.3 * fl, energy=1.3)
    oR.set(tg, flash=0.3 * fl, energy=1.3)
    b = 6 * math.exp(-max(t - (t_ent - 0.05), 0) / 0.12) if t >= t_ent - 0.05 else 0
    burstL.set((-1.25, 0, 0.36), 0.35, b)
    burstR.set((1.25, 0, 0.36), 0.35, b)
    ls = smoother((t - t_ent) / 1.0)
    link_.show(ls > 0.01)
    link_.update(oL.obj.location, oR.obj.location, tg, amp=0.035 * ls, turns=5, strength=1.4 * ls)
    # camera: slow dolly, then pull back for the Nobel line
    k = smoother(t / (t_that + 0.2))
    pb = smoother((t - t_that) / 4.0)
    cam.location = Vector((lerp(0.35, -0.2, k), lerp(-5.7, -5.2, k) - 1.2 * pb, lerp(1.75, 1.35, k) + 0.35 * pb))
    aim(cam, Vector((0, 0, 0.35)))


run(SID, update)
