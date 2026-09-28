"""Shared Blender (bpy 4.5) building blocks for the quantum entanglement film.

Every animated value is computed from shot time t (seconds) inside a
frame_change handler, so any frame can be rendered on its own (resume safe)
and slow motion is a remap of t.
"""
import bpy, math, json, os, sys, time, pathlib
from mathutils import Vector, Euler, Matrix

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEX = ROOT / "tex"
TIMELINE = json.loads((ROOT / "timeline.json").read_text())
FPS = TIMELINE["fps"]

BLUE = (0.10, 0.42, 1.00)
GOLD = (1.00, 0.56, 0.10)
LINK = (0.78, 0.74, 1.00)


def shot_info(shot_id):
    for s in TIMELINE["shots"]:
        if s["id"] == shot_id:
            return s
    raise KeyError(shot_id)


def word_time(shot_id, word, nth=0):
    hits = [w["t"] for w in shot_info(shot_id)["words"] if w["text"].lower().strip(".,") == word.lower()]
    return hits[nth]


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def smoother(x):
    x = clamp(x)
    return x * x * x * (x * (x * 6 - 15) + 10)


def ramp(t, t0, t1):
    return smoother((t - t0) / max(t1 - t0, 1e-6))


def lerp(a, b, f):
    if isinstance(a, (tuple, list, Vector)):
        return Vector([x + (y - x) * f for x, y in zip(a, b)])
    return a + (b - a) * f


def ease_out_expo(x):
    x = clamp(x)
    return 1 if x >= 1 else 1 - 2 ** (-10 * x)


# ------------------------------------------------------------------ scene
def new_scene(res=(1920, 1080), samples=8, frames=100, transparent=False, denoise=False,
              motion_blur=False, exposure=0.0, look="AgX - Punchy"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "CPU"
    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.03
    cy.adaptive_min_samples = 0
    cy.max_bounces = 4
    cy.diffuse_bounces = 1
    cy.glossy_bounces = 2
    cy.transmission_bounces = 4
    cy.transparent_max_bounces = 8
    cy.volume_bounces = 0
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.blur_glossy = 1.0
    cy.sample_clamp_indirect = 6.0
    cy.use_denoising = denoise
    if denoise:
        cy.denoiser = "OPENIMAGEDENOISE"
        cy.denoising_prefilter = "FAST"
        cy.denoising_quality = "BALANCED"
    cy.seed = 1
    cy.use_animated_seed = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, frames
    sc.render.film_transparent = transparent
    sc.render.use_persistent_data = True
    sc.render.use_motion_blur = motion_blur
    sc.render.motion_blur_shutter = 0.5
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    sc.render.image_settings.compression = 15
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = look
    except TypeError:
        pass
    sc.view_settings.exposure = exposure
    sc.render.threads_mode = "AUTO"
    return sc


def world_sky(strength=1.0, rot_z=0.0, rot_x=0.0, path=None, tint=(1, 1, 1)):
    sc = bpy.context.scene
    w = bpy.data.worlds.new("Sky")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    N, L = nt.nodes, nt.links
    bg = N["Background"]
    env = N.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(str(path or TEX / "sky.exr"))
    env.interpolation = "Linear"
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (rot_x, 0, rot_z)
    L.new(tc.outputs["Generated"], mp.inputs["Vector"])
    L.new(mp.outputs["Vector"], env.inputs["Vector"])
    mul = N.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs[0].default_value = 1
    mul.inputs[7].default_value = (*tint, 1)
    L.new(env.outputs["Color"], mul.inputs[6])
    L.new(mul.outputs[2], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    w.cycles_visibility.diffuse = False  # stars should not light the set
    w.cycles_visibility.glossy = True
    return w


def world_hdri(path, strength=1.0, rot_z=0.0, background_color=(0.0, 0.0, 0.0), background_strength=1.0):
    """HDRI lights and reflects, camera sees a plain dark backdrop."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new("HDRI")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    N, L = nt.nodes, nt.links
    out = N["World Output"]
    bg = N["Background"]
    env = N.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(str(path))
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, rot_z)
    L.new(tc.outputs["Generated"], mp.inputs["Vector"])
    L.new(mp.outputs["Vector"], env.inputs["Vector"])
    L.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    bg2 = N.new("ShaderNodeBackground")
    bg2.inputs["Color"].default_value = (*background_color, 1)
    bg2.inputs["Strength"].default_value = background_strength
    lp = N.new("ShaderNodeLightPath")
    mix = N.new("ShaderNodeMixShader")
    L.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    L.new(bg.outputs[0], mix.inputs[1])
    L.new(bg2.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs["Surface"])
    return w


def camera(loc=(0, -8, 0), target=(0, 0, 0), lens=40, fstop=None, focus_obj=None, name="Cam"):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36
    cd.clip_start = 0.01
    cd.clip_end = 1e6
    cam = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = loc
    aim(cam, target)
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        cd.dof.aperture_blades = 7
        cd.dof.aperture_ratio = 1.0
        if focus_obj:
            cd.dof.focus_object = focus_obj
        else:
            cd.dof.focus_distance = (Vector(loc) - Vector(target)).length
    bpy.context.scene.camera = cam
    return cam


def aim_up(obj, target, up):
    f = (Vector(target) - obj.location).normalized()
    x = f.cross(Vector(up)).normalized()
    y = x.cross(f).normalized()
    m = Matrix((x, y, -f)).transposed()
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = m.to_euler()


def aim(obj, target, roll=0.0):
    d = Vector(target) - obj.location
    q = d.to_track_quat("-Z", "Y")
    obj.rotation_mode = "XYZ"
    e = q.to_euler()
    obj.rotation_euler = e
    if roll:
        obj.rotation_euler.rotate_axis("Z", roll)


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location = loc
    return e


def link(obj, parent=None):
    bpy.context.scene.collection.objects.link(obj)
    if parent:
        obj.parent = parent
    return obj


def mesh_obj(name, bm_fn, parent=None):
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bm_fn(bm)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    return link(o, parent)


def uv_sphere(name, radius=1.0, seg=96, rings=48, loc=(0, 0, 0), smooth_shade=True, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=seg, ring_count=rings, location=loc)
    o = bpy.context.object
    o.name = name
    if smooth_shade:
        for p in o.data.polygons:
            p.use_smooth = True
    if parent:
        o.parent = parent
    return o


def set_visible(obj, vis):
    obj.hide_render = not vis
    obj.hide_viewport = not vis


# ------------------------------------------------------------------ materials
def principled(name, color=(0.8, 0.8, 0.8), metallic=0.0, rough=0.4, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    for k, v in kw.items():
        b.inputs[k].default_value = v
    return m


def emission_mat(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    return m, em


def glow_additive_mat(name, color, strength):
    """Emission added on top of transparency: behaves like light, not a solid."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.remove(N["Principled BSDF"])
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    tr = N.new("ShaderNodeBsdfTransparent")
    add = N.new("ShaderNodeAddShader")
    L.new(em.outputs[0], add.inputs[0])
    L.new(tr.outputs[0], add.inputs[1])
    L.new(add.outputs[0], N["Material Output"].inputs["Surface"])
    m.blend_method = "BLEND"
    m.cycles.emission_sampling = "NONE"
    return m, em


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


# ------------------------------------------------------------------ the entangled particle
class Orb:
    """Luminous particle. collapse=0: bright filaments swirling in blue AND gold,
    flickering between the two (undecided). collapse=1: calm, settled in `target`.
    flash adds a white-hot spike."""

    def __init__(self, name, loc=(0, 0, 0), radius=0.35, seed=0.0, parent=None, halo_shell=False):
        self.obj = uv_sphere(name, 1.0, 96, 48, loc, parent=parent)
        self.obj.scale = (radius, radius, radius)
        self.radius = radius
        self.seed = seed
        m = bpy.data.materials.new(name + "_mat")
        m.use_nodes = True
        nt = m.node_tree
        N, L = nt.nodes, nt.links
        N.remove(N["Principled BSDF"])
        out = N["Material Output"]

        def val(label, v):
            n = N.new("ShaderNodeValue")
            n.label = n.name = label
            n.outputs[0].default_value = v
            return n

        def mnode(op, a=None, b=None, va=None, vb=None):
            n = N.new("ShaderNodeMath")
            n.operation = op
            if a is not None:
                L.new(a, n.inputs[0])
            elif va is not None:
                n.inputs[0].default_value = va
            if b is not None:
                L.new(b, n.inputs[1])
            elif vb is not None:
                n.inputs[1].default_value = vb
            return n

        self.w = val("w", seed)
        self.collapse = val("collapse", 0.0)
        self.energy = val("energy", 1.0)
        self.flash = val("flash", 0.0)
        self.bias = val("bias", 0.0)
        self.target = N.new("ShaderNodeRGB")
        self.target.outputs[0].default_value = (*BLUE, 1)

        tc = N.new("ShaderNodeTexCoord")
        oc = N.new("ShaderNodeVectorMath")      # look tuned on a 0.35 sphere; keep it for any size
        oc.operation = "SCALE"
        oc.inputs["Scale"].default_value = 0.35
        L.new(tc.outputs["Object"], oc.inputs[0])
        warp = N.new("ShaderNodeTexNoise")
        warp.noise_dimensions = "4D"
        warp.inputs["Scale"].default_value = 1.5
        warp.inputs["Detail"].default_value = 1.5
        L.new(oc.outputs[0], warp.inputs["Vector"])
        L.new(self.w.outputs[0], warp.inputs["W"])
        calm = N.new("ShaderNodeMapRange")
        calm.inputs[3].default_value = 2.2
        calm.inputs[4].default_value = 0.35
        L.new(self.collapse.outputs[0], calm.inputs[0])
        wsc = N.new("ShaderNodeVectorMath")
        wsc.operation = "SCALE"
        L.new(warp.outputs["Color"], wsc.inputs[0])
        L.new(calm.outputs[0], wsc.inputs["Scale"])
        wadd = N.new("ShaderNodeVectorMath")
        wadd.operation = "ADD"
        L.new(wsc.outputs[0], wadd.inputs[0])
        L.new(oc.outputs[0], wadd.inputs[1])

        # colour field: which regions lean blue, which lean gold
        swirl = N.new("ShaderNodeTexNoise")
        swirl.noise_dimensions = "4D"
        swirl.inputs["Scale"].default_value = 1.9
        swirl.inputs["Detail"].default_value = 2.0
        L.new(wadd.outputs[0], swirl.inputs["Vector"])
        wofs = mnode("ADD", self.w.outputs[0], vb=3.7)
        L.new(wofs.outputs[0], swirl.inputs["W"])
        fbias = mnode("ADD", swirl.outputs["Fac"], self.bias.outputs[0])
        side = N.new("ShaderNodeMapRange")
        side.inputs[1].default_value = 0.44
        side.inputs[2].default_value = 0.56
        L.new(fbias.outputs[0], side.inputs[0])
        cmix = N.new("ShaderNodeMix")
        cmix.data_type = "RGBA"
        L.new(side.outputs[0], cmix.inputs[0])
        cmix.inputs[6].default_value = (*BLUE, 1)
        cmix.inputs[7].default_value = (*GOLD, 1)
        final = N.new("ShaderNodeMix")
        final.data_type = "RGBA"
        L.new(self.collapse.outputs[0], final.inputs[0])
        L.new(cmix.outputs[2], final.inputs[6])
        L.new(self.target.outputs[0], final.inputs[7])

        # thin bright filaments of light, flowing
        fil = N.new("ShaderNodeTexNoise")
        fil.noise_dimensions = "4D"
        fil.inputs["Scale"].default_value = 3.2
        fil.inputs["Detail"].default_value = 3.0
        fil.inputs["Distortion"].default_value = 0.0
        L.new(wadd.outputs[0], fil.inputs["Vector"])
        wfast = mnode("MULTIPLY", self.w.outputs[0], vb=1.6)
        L.new(wfast.outputs[0], fil.inputs["W"])
        ridge = mnode("SUBTRACT", fil.outputs["Fac"], vb=0.5)
        ridge = mnode("ABSOLUTE", ridge.outputs[0])
        ridge2 = N.new("ShaderNodeMapRange")          # 0 at the ridge line -> 1
        ridge2.inputs[1].default_value = 0.0
        ridge2.inputs[2].default_value = 0.07
        ridge2.inputs[3].default_value = 1.0
        ridge2.inputs[4].default_value = 0.0
        L.new(ridge.outputs[0], ridge2.inputs[0])
        filp = mnode("POWER", ridge2.outputs[0], vb=2.0)
        # calm down filaments once collapsed
        fcal = N.new("ShaderNodeMapRange")
        fcal.inputs[3].default_value = 3.2
        fcal.inputs[4].default_value = 1.2
        L.new(self.collapse.outputs[0], fcal.inputs[0])
        filk = mnode("MULTIPLY", filp.outputs[0], fcal.outputs[0])
        # body glow: dim inner light, brighter towards the centre of the disc
        lw = N.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.5
        cosv = mnode("SUBTRACT", va=1.0, b=lw.outputs["Facing"])
        body = mnode("POWER", cosv.outputs[0], vb=1.5)
        bodyk = N.new("ShaderNodeMapRange")
        bodyk.inputs[3].default_value = 0.22
        bodyk.inputs[4].default_value = 1.1
        L.new(self.collapse.outputs[0], bodyk.inputs[0])
        bodyv = mnode("MULTIPLY", body.outputs[0], bodyk.outputs[0])
        sumv = mnode("ADD", bodyv.outputs[0], filk.outputs[0])
        stren = mnode("MULTIPLY", sumv.outputs[0], self.energy.outputs[0])
        stren = mnode("MULTIPLY_ADD", self.flash.outputs[0], None, vb=25.0)
        L.new(self.flash.outputs[0], stren.inputs[0])
        stren_base = mnode("MULTIPLY", sumv.outputs[0], self.energy.outputs[0])
        L.new(stren_base.outputs[0], stren.inputs[2])
        # white-hot core seen through the centre
        core = mnode("POWER", cosv.outputs[0], vb=10.0)
        corek = mnode("MULTIPLY", core.outputs[0], vb=0.55)
        colcore = N.new("ShaderNodeMix")
        colcore.data_type = "RGBA"
        L.new(corek.outputs[0], colcore.inputs[0])
        L.new(final.outputs[2], colcore.inputs[6])
        colcore.inputs[7].default_value = (1.0, 0.95, 0.92, 1)
        flcol = N.new("ShaderNodeMix")
        flcol.data_type = "RGBA"
        L.new(self.flash.outputs[0], flcol.inputs[0])
        L.new(colcore.outputs[2], flcol.inputs[6])
        flcol.inputs[7].default_value = (1, 1, 1, 1)
        em = N.new("ShaderNodeEmission")
        L.new(flcol.outputs[2], em.inputs["Color"])
        L.new(stren.outputs[0], em.inputs["Strength"])
        # glassy skin catches highlights: reads as a physical object
        gl = N.new("ShaderNodeBsdfGlossy")
        gl.inputs["Roughness"].default_value = 0.05
        fr = N.new("ShaderNodeFresnel")
        fr.inputs["IOR"].default_value = 1.5
        mixs = N.new("ShaderNodeMixShader")
        addg = N.new("ShaderNodeAddShader")
        L.new(em.outputs[0], addg.inputs[0])
        L.new(gl.outputs[0], addg.inputs[1])
        L.new(fr.outputs[0], mixs.inputs[0])
        L.new(em.outputs[0], mixs.inputs[1])
        L.new(addg.outputs[0], mixs.inputs[2])
        L.new(mixs.outputs[0], out.inputs["Surface"])
        assign(self.obj, m)
        self.mat = m
        m.cycles.emission_sampling = "NONE"

        # soft corona: additive shell, falls off fast away from the particle
        self.halo = uv_sphere(name + "_halo", 2.4, 48, 24, parent=self.obj)
        hm = bpy.data.materials.new(name + "_halo_mat")
        hm.use_nodes = True
        H, HL = hm.node_tree.nodes, hm.node_tree.links
        H.remove(H["Principled BSDF"])
        hlw = H.new("ShaderNodeLayerWeight")
        hlw.inputs["Blend"].default_value = 0.5
        hinv = H.new("ShaderNodeMath")
        hinv.operation = "SUBTRACT"
        hinv.inputs[0].default_value = 1.0
        HL.new(hlw.outputs["Facing"], hinv.inputs[1])
        # ring profile: zero over the particle's face, peak at its rim, fast falloff outward
        cos0 = math.sqrt(1 - (1 / 2.4) ** 2)
        hx = H.new("ShaderNodeMath")
        hx.operation = "DIVIDE"
        hx.inputs[1].default_value = cos0
        HL.new(hinv.outputs[0], hx.inputs[0])
        hpw = H.new("ShaderNodeMath")
        hpw.operation = "POWER"
        hpw.inputs[1].default_value = 9.0
        HL.new(hx.outputs[0], hpw.inputs[0])
        hlt = H.new("ShaderNodeMath")
        hlt.operation = "LESS_THAN"
        hlt.inputs[1].default_value = 1.0
        HL.new(hx.outputs[0], hlt.inputs[0])
        hpow = H.new("ShaderNodeMath")
        hpow.operation = "MULTIPLY"
        HL.new(hpw.outputs[0], hpow.inputs[0])
        HL.new(hlt.outputs[0], hpow.inputs[1])
        self.halo_k = H.new("ShaderNodeValue")
        self.halo_k.name = "k"
        hm2 = H.new("ShaderNodeMath")
        hm2.operation = "MULTIPLY"
        HL.new(hpow.outputs[0], hm2.inputs[0])
        HL.new(self.halo_k.outputs[0], hm2.inputs[1])
        self.halo_col = H.new("ShaderNodeRGB")
        hem = H.new("ShaderNodeEmission")
        HL.new(self.halo_col.outputs[0], hem.inputs["Color"])
        HL.new(hm2.outputs[0], hem.inputs["Strength"])
        htr = H.new("ShaderNodeBsdfTransparent")
        had = H.new("ShaderNodeAddShader")
        HL.new(hem.outputs[0], had.inputs[0])
        HL.new(htr.outputs[0], had.inputs[1])
        HL.new(had.outputs[0], H["Material Output"].inputs["Surface"])
        assign(self.halo, hm)
        self.halo.hide_render = not halo_shell
        for o in (self.halo,):
            o.visible_shadow = False
            o.visible_diffuse = False
            o.visible_glossy = False
        ld = bpy.data.lights.new(name + "_light", "POINT")
        ld.shadow_soft_size = radius
        ld.energy = 0
        self.light = bpy.data.objects.new(name + "_light", ld)
        link(self.light, self.obj)
        self.light_power = 0.0

    def set_scale(self, f):
        r = self.radius * f
        self.obj.scale = (r, r, r)

    def set(self, t, collapse=0.0, target=None, energy=1.25, flash=0.0, speed=0.5, halo=1.2, flicker=1.0):
        self.w.outputs[0].default_value = self.seed + t * speed
        self.collapse.outputs[0].default_value = collapse
        self.energy.outputs[0].default_value = energy
        self.flash.outputs[0].default_value = flash
        # undecided: the balance swings between mostly blue and mostly gold
        sway = 0.075 * math.sin(2 * math.pi * 0.6 * t + self.seed) + 0.03 * math.sin(2 * math.pi * 1.7 * t + 2 * self.seed)
        self.bias.outputs[0].default_value = sway * flicker * (1 - collapse)
        if target is not None:
            self.target.outputs[0].default_value = (*target, 1)
        undecided = (0.66, 0.6, 1.0)
        hc = lerp(undecided, target or undecided, clamp(collapse))
        self.halo_col.outputs[0].default_value = (*hc, 1)
        self.halo_k.outputs[0].default_value = halo * energy * (1 + 10 * flash)
        if self.light_power:
            self.light.data.color = tuple(hc)
            self.light.data.energy = self.light_power * energy * (1 + 8 * flash)


# ------------------------------------------------------------------ the entanglement link: two strands twisting round each other
class Link:
    def __init__(self, name, n=160, radius=0.012, strength=5.0, color=LINK):
        self.n = n
        self.curves = []
        self.mats = []
        for k in range(2):
            cu = bpy.data.curves.new(f"{name}{k}", "CURVE")
            cu.dimensions = "3D"
            cu.bevel_depth = radius
            cu.bevel_resolution = 3
            cu.use_fill_caps = True
            sp = cu.splines.new("POLY")
            sp.points.add(n - 1)
            o = bpy.data.objects.new(f"{name}{k}", cu)
            link(o)
            m = bpy.data.materials.new(f"{name}{k}_mat")
            m.use_nodes = True
            nt = m.node_tree
            N, L = nt.nodes, nt.links
            N.remove(N["Principled BSDF"])
            tc = N.new("ShaderNodeTexCoord")
            nz = N.new("ShaderNodeTexNoise")
            nz.noise_dimensions = "4D"
            nz.inputs["Scale"].default_value = 3.0
            nz.inputs["Detail"].default_value = 4
            L.new(tc.outputs["Object"], nz.inputs["Vector"])
            wv = N.new("ShaderNodeValue")
            wv.name = "w"
            L.new(wv.outputs[0], nz.inputs["W"])
            mr = N.new("ShaderNodeMapRange")
            mr.inputs[1].default_value = 0.35
            mr.inputs[2].default_value = 0.7
            mr.inputs[3].default_value = 0.25
            mr.inputs[4].default_value = 1.6
            L.new(nz.outputs["Fac"], mr.inputs[0])
            sv = N.new("ShaderNodeValue")
            sv.name = "strength"
            sv.outputs[0].default_value = strength
            mul = N.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            L.new(mr.outputs[0], mul.inputs[0])
            L.new(sv.outputs[0], mul.inputs[1])
            em = N.new("ShaderNodeEmission")
            em.inputs["Color"].default_value = (*color, 1)
            L.new(mul.outputs[0], em.inputs["Strength"])
            tr = N.new("ShaderNodeBsdfTransparent")
            add = N.new("ShaderNodeAddShader")
            L.new(em.outputs[0], add.inputs[0])
            L.new(tr.outputs[0], add.inputs[1])
            L.new(add.outputs[0], N["Material Output"].inputs["Surface"])
            o.data.materials.append(m)
            m.cycles.emission_sampling = "NONE"
            o.visible_shadow = False
            o.visible_diffuse = False
            self.curves.append(o)
            self.mats.append(m)

    def update(self, a, b, t, amp=0.06, turns=6.0, sag=0.0, strength=None, spin=1.2, wobble=0.25):
        a, b = Vector(a), Vector(b)
        L_ = (b - a).length

        def fn(s_):
            p = a.lerp(b, s_)
            p.z -= sag * math.sin(math.pi * s_)
            return p
        self.update_curve(fn, t, amp=amp, turns=turns * max(L_, 0.3) / 2.4, strength=strength, spin=spin, wobble=wobble)

    def update_curve(self, fn, t, amp=0.06, turns=6.0, strength=None, spin=1.2, wobble=0.25, up=(0, 0, 1)):
        """Two strands twisting around the path fn(s), s in [0,1]; `turns` is the total count."""
        upv = Vector(up)
        pts = [fn(i / (self.n - 1)) for i in range(self.n)]
        for k, o in enumerate(self.curves):
            sp = o.data.splines[0]
            for i in range(self.n):
                s_ = i / (self.n - 1)
                tan = (pts[min(i + 1, self.n - 1)] - pts[max(i - 1, 0)])
                if tan.length < 1e-9:
                    tan = Vector((1, 0, 0))
                d = tan.normalized()
                ref = upv if abs(d.dot(upv)) < 0.95 else Vector((1, 0, 0))
                u = d.cross(ref).normalized()
                v = d.cross(u).normalized()
                taper = math.sin(math.pi * s_) ** 0.6
                ang = 2 * math.pi * turns * s_ + t * spin + k * math.pi
                r = amp * taper * (1 + wobble * math.sin(7 * s_ + t * 1.7 + k))
                p = pts[i] + (u * math.cos(ang) + v * math.sin(ang)) * r
                sp.points[i].co = (p.x, p.y, p.z, 1)
            self.mats[k].node_tree.nodes["w"].outputs[0].default_value = t * 0.8 + k * 5
            if strength is not None:
                self.mats[k].node_tree.nodes["strength"].outputs[0].default_value = strength

    def show(self, vis):
        for o in self.curves:
            set_visible(o, vis)


# ------------------------------------------------------------------ soft light burst (reads as light, not a solid ball)
def soft_glow_mat(name, color, power=5.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.remove(N["Principled BSDF"])
    lw = N.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    inv = N.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    L.new(lw.outputs["Facing"], inv.inputs[1])
    pw = N.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = power
    L.new(inv.outputs[0], pw.inputs[0])
    k = N.new("ShaderNodeValue")
    k.name = "k"
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(pw.outputs[0], mul.inputs[0])
    L.new(k.outputs[0], mul.inputs[1])
    col = N.new("ShaderNodeRGB")
    col.name = "col"
    col.outputs[0].default_value = (*color, 1)
    em = N.new("ShaderNodeEmission")
    L.new(col.outputs[0], em.inputs["Color"])
    L.new(mul.outputs[0], em.inputs["Strength"])
    tr = N.new("ShaderNodeBsdfTransparent")
    add = N.new("ShaderNodeAddShader")
    L.new(em.outputs[0], add.inputs[0])
    L.new(tr.outputs[0], add.inputs[1])
    L.new(add.outputs[0], N["Material Output"].inputs["Surface"])
    m.cycles.emission_sampling = "NONE"
    return m, k, col


class Burst:
    def __init__(self, name, color=(0.92, 0.88, 1.0), radius=1.0):
        self.obj = uv_sphere(name, radius, 64, 32)
        self.mat, self.k, self.col = soft_glow_mat(name + "_mat", color, 10.0)
        assign(self.obj, self.mat)
        self.obj.visible_shadow = False
        self.obj.visible_diffuse = False
        self.obj.visible_glossy = False

    def set(self, loc, size, strength, color=None):
        set_visible(self.obj, strength > 1e-3)
        self.obj.location = loc
        self.obj.scale = (size, size, size)
        self.k.outputs[0].default_value = strength
        if color:
            self.col.outputs[0].default_value = (*color, 1)


# ------------------------------------------------------------------ expanding ring of light at a measurement (constant thin tube)
class Shockwave:
    def __init__(self, name, color, n=128, thickness=0.004):
        cu = bpy.data.curves.new(name, "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = thickness
        cu.bevel_resolution = 2
        sp = cu.splines.new("POLY")
        sp.points.add(n - 1)
        sp.use_cyclic_u = True
        self.n = n
        self.obj = bpy.data.objects.new(name, cu)
        link(self.obj)
        self.mat, self.em = glow_additive_mat(name + "_mat", color, 0)
        self.obj.data.materials.append(self.mat)
        self.obj.visible_shadow = False
        self.obj.visible_diffuse = False
        self.obj.visible_glossy = False
        self.obj.cycles.use_motion_blur = False

    def update(self, center, t, t0, radius=0.35, reach=2.2, dur=0.9, strength=12, normal=(0, 0, 1), color=None):
        x = (t - t0) / dur
        if x < 0 or x > 1:
            set_visible(self.obj, False)
            return
        set_visible(self.obj, True)
        r = radius * (1 + ease_out_expo(x) * reach)
        q = Vector(normal).normalized().to_track_quat("Z", "Y")
        sp = self.obj.data.splines[0]
        for i in range(self.n):
            a = 2 * math.pi * i / self.n
            p = q @ Vector((r * math.cos(a), r * math.sin(a), 0)) + Vector(center)
            sp.points[i].co = (p.x, p.y, p.z, 1)
        self.em.inputs["Strength"].default_value = strength * (1 - x) ** 2.5
        if color:
            self.em.inputs["Color"].default_value = (*color, 1)


# ------------------------------------------------------------------ measurement device
class Detector:
    """Brushed titanium ring with inward sensor pads. Rig is an Empty; the ring
    lies in its local XZ plane so the particle sits in the hole when
    the rig sits at the particle."""

    def __init__(self, name, R=0.72):
        import bmesh
        self.rig = empty(name)
        self.R = R
        metal = principled(name + "_ti", (0.60, 0.61, 0.64), 1.0, 0.26, **{"Anisotropic": 0.6})
        dark = principled(name + "_dark", (0.03, 0.03, 0.035), 0.3, 0.45)
        self.pad_mat, self.pad_em = emission_mat(name + "_pad", (0.35, 0.8, 1.0), 0.5)
        self.led_mat, self.led_em = emission_mat(name + "_led", (0.3, 1.0, 0.6), 2.0)
        bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=0.14, major_segments=160, minor_segments=32)
        ring = bpy.context.object
        ring.name = name + "_ring"
        ring.scale = (1, 1, 0.42)
        bpy.ops.object.transform_apply(scale=True)
        for p in ring.data.polygons:
            p.use_smooth = True
        assign(ring, metal)
        ring.rotation_euler = (math.pi / 2, 0, 0)
        ring.parent = self.rig
        bpy.ops.mesh.primitive_torus_add(major_radius=R - 0.1, minor_radius=0.035, major_segments=160, minor_segments=16)
        liner = bpy.context.object
        liner.name = name + "_liner"
        for p in liner.data.polygons:
            p.use_smooth = True
        assign(liner, dark)
        liner.rotation_euler = (math.pi / 2, 0, 0)
        liner.parent = self.rig
        self.pads = []
        for i in range(16):
            a = 2 * math.pi * i / 16
            bpy.ops.mesh.primitive_cube_add(size=1)
            pad = bpy.context.object
            pad.name = f"{name}_pad{i}"
            pad.scale = (0.02, 0.09, 0.05)
            pad.location = ((R - 0.13) * math.cos(a), 0, (R - 0.13) * math.sin(a))
            pad.rotation_euler = (0, -a, 0)
            assign(pad, self.pad_mat)
            pad.parent = self.rig
            self.pads.append(pad)
        for i in range(8):
            a = 2 * math.pi * (i + 0.5) / 8
            bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.16, vertices=32)
            c = bpy.context.object
            c.name = f"{name}_clamp{i}"
            c.location = ((R + 0.15) * math.cos(a), 0, (R + 0.15) * math.sin(a))
            c.rotation_euler = (0, math.pi / 2 - a, 0)
            c.rotation_euler = Euler((0, -a + math.pi / 2, 0))
            assign(c, metal)
            c.parent = self.rig
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.014, segments=16, ring_count=8)
            led = bpy.context.object
            led.location = ((R + 0.24) * math.cos(a), 0, (R + 0.24) * math.sin(a))
            assign(led, self.led_mat)
            led.parent = self.rig
        bpy.ops.mesh.primitive_torus_add(major_radius=R + 0.02, minor_radius=0.006, major_segments=160, minor_segments=8)
        strip = bpy.context.object
        strip.rotation_euler = (math.pi / 2, 0, 0)
        strip.location = (0, -0.06, 0)
        assign(strip, self.pad_mat)
        strip.parent = self.rig

    def set(self, loc, rot=(0, 0, 0), scale=1.0, pad=0.5, pad_color=None):
        self.rig.location = loc
        self.rig.rotation_euler = rot
        self.rig.scale = (scale, scale, scale)
        self.pad_em.inputs["Strength"].default_value = pad
        if pad_color:
            self.pad_em.inputs["Color"].default_value = (*pad_color, 1)


# ------------------------------------------------------------------ Earth
def earth(name="Earth", radius=1.0, sun_dir=(1, -0.3, 0.2), loc=(0, 0, 0), night_strength=2.5, seg=256, night_path=None, atmo_scale=1.025):
    sun_dir = Vector(sun_dir).normalized()
    root = empty(name + "_rig", loc)
    body = uv_sphere(name, radius, seg, seg // 2, parent=root)
    m = bpy.data.materials.new(name + "_mat")
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    day = N.new("ShaderNodeTexImage")
    day.image = bpy.data.images.load(str(TEX / "earth_day.jpg"))
    day.interpolation = "Cubic"
    L.new(tc.outputs["UV"], day.inputs["Vector"])
    L.new(day.outputs["Color"], b.inputs["Base Color"])
    ocean = N.new("ShaderNodeTexImage")
    ocean.image = bpy.data.images.load(str(TEX / "earth_ocean_mask.png"))
    ocean.image.colorspace_settings.name = "Non-Color"
    L.new(tc.outputs["UV"], ocean.inputs["Vector"])
    rr = N.new("ShaderNodeMapRange")
    rr.inputs[3].default_value = 0.75
    rr.inputs[4].default_value = 0.42
    L.new(ocean.outputs["Color"], rr.inputs[0])
    L.new(rr.outputs[0], b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = 0.5
    night = N.new("ShaderNodeTexImage")
    night.image = bpy.data.images.load(str(night_path or TEX / "earth_night.jpg"))
    night.interpolation = "Cubic"
    L.new(tc.outputs["UV"], night.inputs["Vector"])
    # night mask from world-space normal vs sun direction
    geo = N.new("ShaderNodeNewGeometry")
    dotn = N.new("ShaderNodeVectorMath")
    dotn.operation = "DOT_PRODUCT"
    dotn.inputs[1].default_value = sun_dir
    L.new(geo.outputs["Normal"], dotn.inputs[0])
    nm = N.new("ShaderNodeMapRange")
    nm.inputs[1].default_value = 0.08
    nm.inputs[2].default_value = -0.18
    L.new(dotn.outputs["Value"], nm.inputs[0])
    cc = N.new("ShaderNodeMix")
    cc.data_type = "RGBA"
    cc.blend_type = "MULTIPLY"
    cc.inputs[0].default_value = 1
    L.new(night.outputs["Color"], cc.inputs[6])
    cc.inputs[7].default_value = (1.0, 0.72, 0.42, 1)
    L.new(cc.outputs[2], b.inputs["Emission Color"])
    ns = N.new("ShaderNodeMath")
    ns.operation = "MULTIPLY"
    ns.inputs[1].default_value = night_strength
    L.new(nm.outputs[0], ns.inputs[0])
    L.new(ns.outputs[0], b.inputs["Emission Strength"])
    assign(body, m)
    m.cycles.emission_sampling = "NONE"   # city lights must not become 30k light sources
    # clouds
    cl = uv_sphere(name + "_clouds", radius * 1.006, seg, seg // 2, parent=root)
    cm = bpy.data.materials.new(name + "_clouds_mat")
    cm.use_nodes = True
    cn = cm.node_tree
    cb = cn.nodes["Principled BSDF"]
    ci = cn.nodes.new("ShaderNodeTexImage")
    ci.image = bpy.data.images.load(str(TEX / "earth_clouds.jpg"))
    ci.image.colorspace_settings.name = "Non-Color"
    ctc = cn.nodes.new("ShaderNodeTexCoord")
    cn.links.new(ctc.outputs["UV"], ci.inputs["Vector"])
    cr = cn.nodes.new("ShaderNodeMapRange")
    cr.inputs[1].default_value = 0.08
    cr.inputs[2].default_value = 0.9
    cn.links.new(ci.outputs["Color"], cr.inputs[0])
    cn.links.new(cr.outputs[0], cb.inputs["Alpha"])
    cb.inputs["Base Color"].default_value = (0.95, 0.95, 0.97, 1)
    cb.inputs["Roughness"].default_value = 0.9
    cm.blend_method = "BLEND"
    assign(cl, cm)
    # atmosphere: additive rim glow, bright on the day side, bluish, fades on night side
    at = uv_sphere(name + "_atmo", radius * atmo_scale, 256, 128, parent=root)
    am = bpy.data.materials.new(name + "_atmo_mat")
    am.use_nodes = True
    an = am.node_tree
    A, AL = an.nodes, an.links
    A.remove(A["Principled BSDF"])
    lw = A.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    pw = A.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 3.0
    AL.new(lw.outputs["Facing"], pw.inputs[0])
    g2 = A.new("ShaderNodeNewGeometry")
    d2 = A.new("ShaderNodeVectorMath")
    d2.operation = "DOT_PRODUCT"
    d2.inputs[1].default_value = sun_dir
    AL.new(g2.outputs["Normal"], d2.inputs[0])
    dm = A.new("ShaderNodeMapRange")
    dm.inputs[1].default_value = -0.35
    dm.inputs[2].default_value = 0.35
    AL.new(d2.outputs["Value"], dm.inputs[0])
    mm = A.new("ShaderNodeMath")
    mm.operation = "MULTIPLY"
    AL.new(pw.outputs[0], mm.inputs[0])
    AL.new(dm.outputs[0], mm.inputs[1])
    ms = A.new("ShaderNodeMath")
    ms.operation = "MULTIPLY"
    ms.inputs[1].default_value = 3.0
    AL.new(mm.outputs[0], ms.inputs[0])
    em = A.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.28, 0.55, 1.0, 1)
    AL.new(ms.outputs[0], em.inputs["Strength"])
    tr = A.new("ShaderNodeBsdfTransparent")
    ad = A.new("ShaderNodeAddShader")
    AL.new(em.outputs[0], ad.inputs[0])
    AL.new(tr.outputs[0], ad.inputs[1])
    AL.new(ad.outputs[0], A["Material Output"].inputs["Surface"])
    assign(at, am)
    am.cycles.emission_sampling = "NONE"
    at.visible_shadow = False
    at.visible_diffuse = False
    at.visible_glossy = False
    return root, body, cl, at


def latlon_to_vec(lat, lon, r=1.0):
    """Blender UV sphere with equirect texture: lon 0 at -X? Solved empirically
    in calibrate: u = 0.5 + lon/360 maps to angle phi = (u)*2pi - pi about +Z from -X."""
    la, lo = math.radians(lat), math.radians(lon)
    # UV sphere u=0 starts at +X... use the calibrated convention below
    phi = lo + math.pi  # u=0 is lon=-180
    return Vector((r * math.cos(la) * math.cos(phi) * -1, r * math.cos(la) * math.sin(phi) * -1, r * math.sin(la)))


def sun(direction=(1, -0.3, 0.2), strength=4.0, angle_deg=0.53, color=(1.0, 0.97, 0.92)):
    ld = bpy.data.lights.new("Sun", "SUN")
    ld.energy = strength
    ld.angle = math.radians(angle_deg)
    ld.color = color
    o = bpy.data.objects.new("Sun", ld)
    link(o)
    o.rotation_euler = (-Vector(direction)).to_track_quat("-Z", "Y").to_euler()
    return o


def area_light(name, loc, target, size=2.0, power=200, color=(1, 1, 1), shape="DISK"):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = power
    ld.size = size
    ld.shape = shape
    ld.color = color
    o = bpy.data.objects.new(name, ld)
    link(o)
    o.location = loc
    aim(o, target)
    return o


# ------------------------------------------------------------------ render driver
def run(shot_id, update, out_dir=None, frames=None, time_map=None):
    """Register update(t) as a frame handler and render missing frames.
    argv after '--': [start end] to render a sub-range."""
    sc = bpy.context.scene
    out = pathlib.Path(os.environ.get("QE_OUT") or out_dir or (ROOT / "renders" / shot_id))
    out.mkdir(parents=True, exist_ok=True)
    tmap = time_map or (lambda f: (f - 1) / FPS)

    def handler(scene, depsgraph=None):
        f = scene.frame_current + scene.frame_subframe
        update(tmap(f))

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(handler)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    argv = [a for a in argv if not a.startswith("--")]
    lo, hi = sc.frame_start, sc.frame_end
    only = None
    if len(argv) >= 2:
        lo, hi = int(argv[0]), int(argv[1])
    if len(argv) >= 3 and argv[2] == "still":
        only = [lo]
    frames = only or list(range(lo, hi + 1))
    if os.environ.get("QE_TRACK"):
        # export per-frame screen positions of named objects instead of rendering
        from bpy_extras.object_utils import world_to_camera_view
        names = os.environ["QE_TRACK"].split(",")
        W, H = sc.render.resolution_x, sc.render.resolution_y
        data = {"w": W, "h": H, "frames": {}}
        for f in range(sc.frame_start, sc.frame_end + 1):
            sc.frame_set(f)
            bpy.context.view_layer.update()
            row = {}
            for nm in names:
                o = bpy.data.objects.get(nm)
                if o is None:
                    continue
                v = world_to_camera_view(sc, sc.camera, o.matrix_world.translation)
                row[nm] = [round(v.x * W, 1), round((1 - v.y) * H, 1), round(v.z, 3)]
            data["frames"][f] = row
        tdir = ROOT / "tracks"
        tdir.mkdir(exist_ok=True)
        (tdir / f"{shot_id}.json").write_text(json.dumps(data))
        print(f"TRACKED {shot_id}", flush=True)
        os._exit(0)
    if os.environ.get("QE_SAMPLES"):
        sc.cycles.samples = int(os.environ["QE_SAMPLES"])
    if os.environ.get("QE_NODOF") and sc.camera:
        sc.camera.data.dof.use_dof = False
    if os.environ.get("QE_NOEMS"):
        for m in bpy.data.materials:
            m.cycles.emission_sampling = "NONE"
    if os.environ.get("QE_NOTREE"):
        sc.cycles.use_light_tree = False
    for nm in (os.environ.get("QE_HIDE") or "").split(","):
        if nm:
            for o in bpy.data.objects:
                if o.name.startswith(nm):
                    o.hide_render = True
    if os.environ.get("QE_RES"):
        sc.render.resolution_percentage = int(os.environ["QE_RES"])
    if os.environ.get("QE_NOHALO"):
        for o in bpy.data.objects:
            if "_halo" in o.name:
                o.hide_render = True
    for f in frames:
        path = out / f"{f:04d}.png"
        if path.exists() and path.stat().st_size > 1000:
            continue
        t0 = time.time()
        sc.frame_set(f)
        sc.render.filepath = str(out / f"{f:04d}.tmp.png")
        bpy.ops.render.render(write_still=True)
        os.replace(out / f"{f:04d}.tmp.png", path)
        print(f"RENDERED {shot_id} {f}/{hi} {time.time() - t0:.1f}s", flush=True)
    print(f"DONE {shot_id}", flush=True)
    sys.stdout.flush()
    os._exit(0)  # bpy as a module can hang on interpreter teardown


# ------------------------------------------------------------------ drifting specks: "everything is made of tiny particles"
def speck_field(n=520, seed=3, xr=(-5, 5), yr=(-32, 9), zr=(-2.6, 2.6)):
    import random
    rnd = random.Random(seed)
    mats = [glow_additive_mat(f"speck{k}", c, st)[0] for k, (c, st) in enumerate(
        [((0.75, 0.82, 1.0), 3.0), ((1.0, 0.8, 0.6), 2.6), ((0.6, 0.7, 1.0), 3.6), ((0.9, 0.9, 1.0), 2.0)])]
    out = []
    for i in range(n):
        p = Vector((rnd.uniform(*xr), rnd.uniform(*yr), rnd.uniform(*zr)))
        if p.length < 1.6:
            continue
        o = uv_sphere(f"speck{i}", rnd.uniform(0.005, 0.02), 10, 6, p)
        assign(o, mats[rnd.randrange(4)])
        o.visible_shadow = False
        o.visible_diffuse = False
        o.visible_glossy = False
        out.append((o, p, rnd.uniform(0, 6.283), rnd.uniform(0.6, 1.4)))
    return out


def update_specks(specks, t):
    for o, p, ph, sp in specks:
        o.location = p + Vector((0.06 * math.sin(t * 0.21 * sp + ph), 0.05 * math.cos(t * 0.17 * sp + ph), 0.06 * math.sin(t * 0.13 * sp + 2 * ph)))


def calibrate_geo(obj, radius):
    """Return geo(lat, lon, r) -> local position for a UV sphere carrying an equirect map
    (u = (lon + 180) / 360, v = (lat + 90) / 180). Fitted from the mesh's own UVs."""
    me = obj.data
    uvl = me.uv_layers.active.data
    best = None
    for pi_ in range(0, len(me.polygons), 37):
        poly = me.polygons[pi_]
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            co = me.vertices[vi].co
            u = uvl[li].uv[0]
            if abs(co.z) > 0.8 * co.length or u < 0.05 or u > 0.95:
                continue
            ang = math.atan2(co.y, co.x)
            for sgn in (1, -1):
                off = (ang - sgn * 2 * math.pi * u) % (2 * math.pi)
                best = best or {}
                best.setdefault(sgn, []).append(off)
    # choose sign with the most consistent offset
    def spread(v):
        c = sum(math.cos(x) for x in v) / len(v)
        s_ = sum(math.sin(x) for x in v) / len(v)
        return math.hypot(c, s_), math.atan2(s_, c)
    (r1, o1), (r2, o2) = spread(best[1]), spread(best[-1])
    sgn, off = (1, o1) if r1 > r2 else (-1, o2)

    def geo(lat, lon, r=None):
        rr = r if r is not None else radius
        u = (lon + 180.0) / 360.0
        a = sgn * 2 * math.pi * u + off
        la = math.radians(lat)
        return Vector((rr * math.cos(la) * math.cos(a), rr * math.cos(la) * math.sin(a), rr * math.sin(la)))
    return geo
