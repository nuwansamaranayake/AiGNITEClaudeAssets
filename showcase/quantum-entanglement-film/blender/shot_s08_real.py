"""S08: 'In 2017, a satellite sent entangled particles of light to two ground stations,
1,200 km apart.' Micius over night-time western China: beams to Delingha and Lijiang.
Units: 1 = 1000 km. The satellite model uses forced perspective (placed on the camera ray
to its true orbital position), so the straight beams project exactly as they would."""
import sys, math, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from qe_lib import *

SID = "s08_real"
info = shot_info(SID)
N = info["frames"]
T = N / FPS
R = 6.371
sc = new_scene((1600, 900), samples=8, frames=N, motion_blur=False, exposure=0.2)
sc.cycles.transparent_max_bounces = 12
world_sky(strength=0.75, rot_z=3.3, rot_x=0.5)

# stations (published coordinates of the Micius ground stations)
DELINGHA = (37.378, 97.729)
LIJIANG = (26.694, 100.030)

rig, body, clouds, atmo = earth(radius=R, sun_dir=(1, 0, 0), night_strength=3.2, seg=512,
                                night_path=TEX / "earth_night_hi.jpg", atmo_scale=1.011)
geo = calibrate_geo(body, R)
clouds.hide_render = True          # night side: clouds are invisible and cost 40% of render time
st1, st2 = geo(*DELINGHA), geo(*LIJIANG)
n_mid = (st1 + st2).normalized()
M = n_mid * R
MID = ((DELINGHA[0] + LIJIANG[0]) / 2, (DELINGHA[1] + LIJIANG[1]) / 2)
east = (geo(MID[0], MID[1] + 0.5) - geo(*MID)).normalized()
east = (east - n_mid * east.dot(n_mid)).normalized()
north = n_mid.cross(east).normalized()
if north.dot(st1 - st2) < 0:
    north = -north
view_t = -east                                                    # we look west, across the two stations
sun_dir = (n_mid * -0.40 + view_t * 0.92).normalized()            # dusk glow just beyond the horizon
for m in (body.active_material, atmo.active_material):
    for nd in m.node_tree.nodes:
        if nd.bl_idname == "ShaderNodeVectorMath" and nd.operation == "DOT_PRODUCT":
            nd.inputs[1].default_value = sun_dir
sun(sun_dir, strength=4.0)
key = sun(n_mid * 0.6 + east * 0.8 + north * 0.3, strength=3.0, color=(1.0, 0.96, 0.9))
sat_coll = bpy.data.collections.new("SatParts")
bpy.context.scene.collection.children.link(sat_coll)

# ------------------------------------------------ satellite (Micius-like: gold-foil bus, two solar wings, telescope)
sat = empty("Sat")
foil = bpy.data.materials.new("foil")
foil.use_nodes = True
fn = foil.node_tree
fb = fn.nodes["Principled BSDF"]
fb.inputs["Base Color"].default_value = (1.0, 0.70, 0.28, 1)
fb.inputs["Metallic"].default_value = 1.0
fb.inputs["Roughness"].default_value = 0.22
ftc = fn.nodes.new("ShaderNodeTexCoord")
fno = fn.nodes.new("ShaderNodeTexNoise")
fno.inputs["Scale"].default_value = 9.0
fno.inputs["Detail"].default_value = 10
fn.links.new(ftc.outputs["Object"], fno.inputs["Vector"])
fbump = fn.nodes.new("ShaderNodeBump")
fbump.inputs["Strength"].default_value = 0.55
fn.links.new(fno.outputs["Fac"], fbump.inputs["Height"])
fn.links.new(fbump.outputs["Normal"], fb.inputs["Normal"])
cell = bpy.data.materials.new("cells")
cell.use_nodes = True
cn = cell.node_tree
cb = cn.nodes["Principled BSDF"]
cb.inputs["Metallic"].default_value = 0.6
cb.inputs["Roughness"].default_value = 0.18
br = cn.nodes.new("ShaderNodeTexBrick")
br.inputs["Scale"].default_value = 6.0
br.inputs["Mortar Size"].default_value = 0.012
br.inputs["Color1"].default_value = (0.015, 0.03, 0.09, 1)
br.inputs["Color2"].default_value = (0.02, 0.035, 0.1, 1)
br.inputs["Mortar"].default_value = (0.55, 0.56, 0.6, 1)
br.offset = 0.0
ctc = cn.nodes.new("ShaderNodeTexCoord")
cn.links.new(ctc.outputs["UV"], br.inputs["Vector"])
cn.links.new(br.outputs["Color"], cb.inputs["Base Color"])
white = principled("sat_white", (0.8, 0.8, 0.82), 0.1, 0.35)
dark = principled("sat_dark", (0.01, 0.01, 0.012), 0.0, 0.3)
alum = principled("sat_alu", (0.7, 0.71, 0.73), 1.0, 0.3)


def part(prim, loc, scale, mat, rot=(0, 0, 0), **kw):
    getattr(bpy.ops.mesh, prim)(location=loc, rotation=rot, **kw)
    o = bpy.context.object
    o.scale = scale
    assign(o, mat)
    o.parent = sat
    return o


part("primitive_cube_add", (0, 0, 0), (0.5, 0.5, 0.7), foil)
part("primitive_cylinder_add", (0, 0, 1.05), (0.32, 0.32, 0.4), white, vertices=48)
part("primitive_cylinder_add", (0, 0, 1.46), (0.27, 0.27, 0.02), dark, vertices=48)
for sgn in (1, -1):
    part("primitive_cylinder_add", (sgn * 0.9, 0, 0.1), (0.03, 0.03, 0.45), alum, rot=(0, math.pi / 2, 0), vertices=16)
    for i in range(2):
        x = sgn * (1.45 + i * 1.12)
        part("primitive_plane_add", (x, 0, 0.1), (0.54, 0.9, 1), cell, rot=(math.pi / 2, 0, 0))
part("primitive_cylinder_add", (0.28, -0.52, -0.35), (0.12, 0.12, 0.05), alum, rot=(math.pi / 2, 0, 0), vertices=32)
for o in sat.children:
    for p in o.data.polygons:
        p.use_smooth = o.data.materials[0] is not cell
    sat_coll.objects.link(o)
try:  # key light touches only the satellite, never the night-side Earth
    key.light_linking.receiver_collection = sat_coll
    print("LIGHTLINK ok")
except Exception as e:
    print("LIGHTLINK unavailable:", e)
    key.data.energy = 0.0

# ------------------------------------------------ beams, pulses, station markers
beam_mat, beam_em = glow_additive_mat("beam", (0.78, 0.72, 1.0), 0.0)
haze_mat, haze_em = glow_additive_mat("haze", (0.6, 0.55, 1.0), 0.0)


def tube(name, mat, n=64):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 1.0
    cu.bevel_resolution = 2
    sp = cu.splines.new("POLY")
    sp.points.add(n - 1)
    o = bpy.data.objects.new(name, cu)
    link(o)
    o.data.materials.append(mat)
    o.visible_shadow = False
    o.visible_diffuse = False
    o.visible_glossy = False
    return o


beams = [tube(f"beam{i}", beam_mat) for i in range(2)]
pulses = [[Orb(f"pulse{k}_{i}", radius=1.0, seed=k * 1.7 + i * 5) for i in range(2)] for k in range(4)]
for pair in pulses:
    for o_ in pair:
        o_.obj.visible_diffuse = False
        o_.obj.visible_glossy = False
        o_.obj.visible_shadow = False
markers = []
for i, st in enumerate((st1, st2)):
    mk = Burst(f"marker{i}", (0.8, 0.75, 1.0))
    wv = Shockwave(f"stwave{i}", (0.8, 0.75, 1.0), thickness=1.0)
    markers.append((mk, wv))

cam = camera(M + east * 2.4 + n_mid * 1.2, M, lens=30)
cam.data.clip_start = 0.0008
TG0 = info["start"] / FPS
t_sat = word_time(SID, "satellite")
t_sent = word_time(SID, "sent")
t_two = word_time(SID, "two")
PERIOD, TRAVEL = 0.75, 0.55


def update(t):
    tg = TG0 + t
    k = smoother(t / T)
    kb = smoother((t - 10.5) / (T - 10.5))
    cp = M + east * lerp(2.3, 2.9, k) + n_mid * lerp(1.25, 1.95, kb) + north * lerp(-0.25, 0.25, k)
    cam.location = cp
    look = M - east * lerp(0.9, 1.4, k) + n_mid * lerp(0.05, 0.25, kb)
    aim_up(cam, look, cp.normalized())
    cam.data.lens = lerp(30, 26, kb)
    # satellite: true orbit 500 km up, drifting north; drawn 20 km from the camera on the same ray
    sat_true = M * ((R + 0.5) / R) + north * lerp(-0.2, 0.12, t / T) + east * 0.55
    ray = (sat_true - cp).normalized()
    D = 0.02
    sat.location = cp + ray * D
    s_draw = 0.0008
    sat.scale = (s_draw, s_draw, s_draw)
    upv = sat_true.normalized()
    to_cam = (cp - sat_true)
    to_cam = (to_cam - upv * to_cam.dot(upv)).normalized()
    fwd = upv.cross(to_cam).normalized()
    down = -upv                                                    # telescope points at the ground
    m3 = Matrix((to_cam.cross(down).normalized(), to_cam, down)).transposed()
    sat.rotation_euler = m3.to_euler()
    sat.rotation_euler.rotate_axis("Z", 0.75 + 0.03 * t)
    sat_mw = Matrix.Translation(sat.location) @ sat.rotation_euler.to_matrix().to_4x4() @ Matrix.Scale(s_draw, 4)
    origin = sat_mw @ Vector((0, 0, 1.46))
    # beams switch on at "sent"
    on = smoother((t - (t_sent - 0.15)) / 0.4)
    for i, st in enumerate((st1, st2)):
        a, b = origin, st
        for tb, rad, em, s_ in ((beams[i], 0.0007, beam_em, 4.0),):
            sp = tb.data.splines[0]
            n = len(sp.points)
            for j in range(n):
                f = j / (n - 1) * on
                p = a.lerp(b, f)
                sp.points[j].co = (p.x, p.y, p.z, 1)
                sp.points[j].radius = rad * max((p - cp).length, 0.02)
            em.inputs["Strength"].default_value = s_ * on
            set_visible(tb, on > 0.01)
    # entangled pairs: one particle down each beam at the same time
    for kk, pair in enumerate(pulses):
        for i, (orb, st) in enumerate(zip(pair, (st1, st2))):
            best = None
            for m in range(40):
                t0 = t_sent + 0.2 + (kk + 4 * m) * PERIOD
                x = (t - t0) / TRAVEL
                if 0 <= x <= 1:
                    best = x
            if best is None or on < 0.5:
                set_visible(orb.obj, False)
                continue
            set_visible(orb.obj, True)
            p = origin.lerp(st, best)
            orb.obj.location = p
            orb.set_scale(0.006 * (p - cp).length)
            orb.set(tg, energy=2.4)
    # station markers light up on "two ground stations" and flash as pairs arrive
    mk_on = smoother((t - (t_two - 0.2)) / 0.5)
    for i, (st, (mk, wv)) in enumerate(zip((st1, st2), markers)):
        d = (st - cp).length
        hit = 0.0
        for m in range(60):
            ta = t_sent + 0.2 + m * PERIOD + TRAVEL
            if 0 <= t - ta < 0.6:
                hit = max(hit, math.exp(-(t - ta) / 0.15))
        mk.set(st * 1.0015, 0.007 * d, (1.5 + 6 * hit) * max(mk_on, on * 0.4))
        set_visible(wv.obj, False)


run(SID, update)
