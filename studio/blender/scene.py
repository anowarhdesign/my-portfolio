"""Anowar's studio, built in code. Run: blender -b -P scene.py -- <stage> [opts]
Stages: preview | bake | env | export | all.   Opts: res=2048 spp=96 only=0,1,2
Coordinates: X right, Y away from the viewer (back wall at y=0, room is y<0), Z up. Units: metres."""
import bpy, bmesh, math, sys, json, os, time
import numpy as np
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEX = os.path.join(ROOT, "tex")
OUT = os.path.join(ROOT, "baked")
RAW = os.path.join(ROOT, "raw")
os.makedirs(OUT, exist_ok=True); os.makedirs(RAW, exist_ok=True)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["preview"]
STAGE = argv[0]
OPT = dict(a.split("=") for a in argv[1:] if "=" in a)
RES = int(OPT.get("res", 2048)); SPP = int(OPT.get("spp", 96))
ONLY = [int(x) for x in OPT["only"].split(",")] if "only" in OPT else [0, 1]
R = math.radians

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
col = scene.collection

# ───────────────────────── materials ─────────────────────────
def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def hexc(h):
    h = h.lstrip("#")
    return tuple(lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (1.0,)

MATS = {}
def mat(name, color="#808080", rough=0.7, tex=None, emit=None, strength=0.0, refl=0.0, emit_tex=None, alpha=1.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = hexc(color)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Specular IOR Level"].default_value = 0.25
    if tex:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(os.path.join(TEX, tex), check_existing=True)
        nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    if emit:
        bsdf.inputs["Emission Color"].default_value = hexc(emit)
        bsdf.inputs["Emission Strength"].default_value = strength
        bsdf.inputs["Base Color"].default_value = (0, 0, 0, 1)
        if emit_tex:
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(os.path.join(TEX, emit_tex), check_existing=True)
            nt.links.new(t.outputs["Color"], bsdf.inputs["Emission Color"])
    m["refl"] = float(refl)
    m["em"] = float(strength)
    m["alpha"] = float(alpha)
    MATS[name] = m
    return m

# ───────────────────────── geometry builder ─────────────────────────
class B:
    """Accumulates primitives into one mesh (one object, one material)."""
    def __init__(self):
        self.bm = bmesh.new()

    def _emit(self, t, loc=(0, 0, 0), rot=(0, 0, 0), smooth=False):
        M = Matrix.Translation(loc) @ Euler(rot, "XYZ").to_matrix().to_4x4()
        bmesh.ops.transform(t, matrix=M, verts=t.verts)
        if smooth:
            for f in t.faces:
                f.smooth = True
        me = bpy.data.meshes.new("tmp")
        t.to_mesh(me); t.free()
        self.bm.from_mesh(me)
        bpy.data.meshes.remove(me)
        return self

    def box(self, size, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.0, seg=2):
        t = bmesh.new()
        bmesh.ops.create_cube(t, size=1.0)
        bmesh.ops.scale(t, vec=size, verts=t.verts)
        if bevel:
            bmesh.ops.bevel(t, geom=t.edges[:], offset=min(bevel, min(size) * 0.45), segments=seg, affect="EDGES", profile=0.5)
        return self._emit(t, loc, rot, smooth=bool(bevel))

    def cyl(self, r, h, loc=(0, 0, 0), rot=(0, 0, 0), seg=24, r2=None, cap=True):
        t = bmesh.new()
        bmesh.ops.create_cone(t, cap_ends=cap, cap_tris=False, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
        return self._emit(t, loc, rot, smooth=True)

    def sphere(self, r, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), seg=20):
        t = bmesh.new()
        bmesh.ops.create_uvsphere(t, u_segments=seg, v_segments=seg // 2, radius=r)
        bmesh.ops.scale(t, vec=scale, verts=t.verts)
        return self._emit(t, loc, rot, smooth=True)

    def plane(self, sx, sz, loc=(0, 0, 0), rot=(0, 0, 0)):
        """Vertical plane in XZ facing -Y, with 0..1 UVs."""
        t = bmesh.new()
        uv = t.loops.layers.uv.new("UVMap")
        vs = [t.verts.new(p) for p in [(-sx / 2, 0, -sz / 2), (sx / 2, 0, -sz / 2), (sx / 2, 0, sz / 2), (-sx / 2, 0, sz / 2)]]
        f = t.faces.new(vs)
        for l, u in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            l[uv].uv = u
        return self._emit(t, loc, rot)

    def tube(self, pts, r, seg=8, closed=False):
        """Round tube along a polyline."""
        t = bmesh.new()
        pts = [Vector(p) for p in pts]
        n = len(pts)
        rings = []
        up = Vector((0, 0, 1))
        for i, p in enumerate(pts):
            a = pts[(i - 1) % n] if (closed or i > 0) else p
            b = pts[(i + 1) % n] if (closed or i < n - 1) else p
            d = (b - a).normalized() if (b - a).length > 1e-9 else Vector((0, 0, 1))
            side = d.cross(up)
            if side.length < 1e-4:
                side = d.cross(Vector((1, 0, 0)))
            side.normalize()
            nrm = side.cross(d).normalized()
            rings.append([t.verts.new(p + (side * math.cos(k / seg * 2 * math.pi) + nrm * math.sin(k / seg * 2 * math.pi)) * r) for k in range(seg)])
        last = n if closed else n - 1
        for i in range(last):
            ra, rb = rings[i], rings[(i + 1) % n]
            for k in range(seg):
                f = t.faces.new([ra[k], ra[(k + 1) % seg], rb[(k + 1) % seg], rb[k]])
                f.smooth = True
        if not closed:
            t.faces.new(rings[0][::-1]); t.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(t, faces=t.faces[:])
        return self._emit(t)

    def _blade(self, rows, loc, rot):
        """rows: list of (v, [5 points across]) -> quads with UVs (u across, v along)."""
        t = bmesh.new(); uv = t.loops.layers.uv.new("UVMap"); vr = []
        for v, pts in rows:
            vr.append((v, [t.verts.new(q) for q in pts]))
        for (va, a), (vb, b) in zip(vr, vr[1:]):
            for k in range(4):
                f = t.faces.new([a[k], a[k + 1], b[k + 1], b[k]]); f.smooth = True
                for l, q in zip(f.loops, [(k / 4, va), ((k + 1) / 4, va), ((k + 1) / 4, vb), (k / 4, vb)]):
                    l[uv].uv = q
        return self._emit(t, loc, rot)

    def heart(self, length, width, loc, rot, fold=0.16, bend=0.4):
        """A pothos leaf: rounded heart with two lobes behind the stem, cupped, drooping tip (local +Y)."""
        prof = [(0.0, 0.34), (0.05, 0.74), (0.13, 0.95), (0.26, 1.0), (0.42, 0.93), (0.58, 0.78), (0.72, 0.58), (0.84, 0.38), (0.93, 0.18), (1.0, 0.0)]
        rows = []
        for u, wf in prof:
            w = width * wf; y = length * u; z = -bend * length * u * u
            back = 0.12 * length * max(0.0, 1 - u / 0.16)      # the lobes sweep back past the stem
            pts = []
            for sx in (-1, -0.5, 0, 0.5, 1):
                pts.append((sx * w / 2, y - back * abs(sx) ** 1.5, z + w * fold * abs(sx) ** 1.6))
            rows.append((u, pts))
        return self._blade(rows, loc, rot)

    def leaf(self, length, width, loc, rot, fold=0.25, bend=0.3, n=5, twist=0.0):
        """A leaf blade: pointed strip, cupped, with a droop and an optional twist along its length (local +Y)."""
        rows = []
        for i in range(n + 1):
            u = i / n
            w = width * math.sin(math.pi * min(1.0, u * 0.92 + 0.08)) ** 0.75 * (1 - u ** 3 * 0.9)
            y = length * u; z = -bend * length * u * u
            c, sn = math.cos(twist * u), math.sin(twist * u)
            pts = []
            for sx in (-1, -0.5, 0, 0.5, 1):
                x0 = sx * w / 2; z0 = abs(w) * fold * abs(sx) ** 1.6
                pts.append((x0 * c - z0 * sn, y, z + x0 * sn + z0 * c))
            rows.append((u, pts))
        return self._blade(rows, loc, rot)

    def done(self, name, material, lm=-1, loc=(0, 0, 0), rot=(0, 0, 0), sharp=40, uv=None):
        me = bpy.data.meshes.new(name)
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:]) if not name.startswith(("screen", "print", "plaque", "win__sky")) else None
        self.bm.to_mesh(me); self.bm.free()
        if "UVMap" not in me.uv_layers:
            me.uv_layers.new(name="UVMap")
        me.uv_layers.new(name="LM")
        me.uv_layers["UVMap"].active_render = True
        me.set_sharp_from_angle(angle=R(sharp))
        o = bpy.data.objects.new(name, me)
        o.location = loc; o.rotation_euler = rot
        col.objects.link(o)
        me.materials.append(material)
        o["lm"] = lm
        if uv:
            planar_uv(o, *uv)
        return o

def planar_uv(o, ax_u, ax_v, scale):
    """World-space planar UVs on UVMap: u = pos[ax_u]/scale, v = pos[ax_v]/scale."""
    me = o.data
    uvl = me.uv_layers["UVMap"].data
    M = Matrix.Translation(o.location) @ o.rotation_euler.to_matrix().to_4x4()
    for poly in me.polygons:
        for li in poly.loop_indices:
            p = M @ me.vertices[me.loops[li].vertex_index].co
            uvl[li].uv = (p[ax_u] / scale[0], p[ax_v] / scale[1])

def box_uv(o, scale):
    """Per-face dominant-axis projection, for wood on boxy furniture."""
    me = o.data
    uvl = me.uv_layers["UVMap"].data
    M = Matrix.Translation(o.location) @ o.rotation_euler.to_matrix().to_4x4()
    for poly in me.polygons:
        n = poly.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        u, v = [(1, 2), (0, 2), (0, 1)][ax]
        for li in poly.loop_indices:
            p = M @ me.vertices[me.loops[li].vertex_index].co
            uvl[li].uv = (p[u] / scale[0], p[v] / scale[1])

def light(name, kind, loc, rot, color, power, size=(0.2, 0.2), spread=180):
    d = bpy.data.lights.new(name, "AREA")
    d.shape = "RECTANGLE"; d.size, d.size_y = size
    d.color = color; d.energy = power; d.spread = R(spread)
    o = bpy.data.objects.new(name, d)
    o.location = loc; o.rotation_euler = rot
    col.objects.link(o)
    o["kind"] = kind
    return o

# ───────────────────────── palette ─────────────────────────
M_WALL = mat("wall", "#CFD3AE", 0.92)
M_CEIL = mat("ceiling", "#ECE9E0", 0.95)
M_FLOOR = mat("floor", "#96684A", 0.55, tex="floor.jpg", refl=0.12)
M_TRIM = mat("trim", "#EDEAE2", 0.6)
M_DESK = mat("desk_top", "#1B1B1E", 0.38, refl=0.30)
M_BLK = mat("black", "#222226", 0.5, refl=0.10)
M_BLK2 = mat("black_soft", "#303035", 0.8)
M_BIRCH = mat("birch", "#DEBE94", 0.6, tex="birch.jpg", refl=0.06)
M_WALNUT = mat("walnut", "#70402A", 0.55, tex="walnut.jpg", refl=0.08)
M_SILVER = mat("silver", "#C4C7CC", 0.35, refl=0.35)
M_BEZEL = mat("bezel", "#0C0C0D", 0.35, refl=0.22)
M_KEY = mat("keycap", "#26262A", 0.6)
M_KEYE = mat("keycap_ember", "#F14E1C", 0.55)
M_MAT = mat("deskmat", "#2A2B30", 0.95)
M_POT = mat("pot", "#ECEAE4", 0.45, refl=0.12)
M_SOIL = mat("soil", "#241A14", 1.0)
M_LEAF = mat("leaf", "#3E8744", 0.55, refl=0.06, tex="leaf.jpg")
M_LEAF3 = mat("leaf_light", "#79B257", 0.55, refl=0.06, tex="leaf_light.jpg")
M_LEAF2 = mat("leaf_dark", "#24603A", 0.5, refl=0.08, tex="leaf_dark.jpg")
M_STEM = mat("stem", "#2E6A3C", 0.6)
M_ROPE = mat("rope", "#DACFB8", 0.95)
M_PEG = mat("pegboard", "#1E1E21", 0.7, tex="pegboard.png")
M_BOOK = mat("book", "#5652E0", 0.6, tex="book.jpg")
M_PAGES = mat("pages", "#EFEBDD", 0.9)
M_GLASSY = mat("glassy", "#0B0B0D", 0.12, refl=0.6)
M_GRAPH = mat("graphite", "#55575C", 0.5, refl=0.1)
M_TABLET = mat("tablet", "#3A3B41", 0.6, refl=0.10)
M_EMBER = mat("ember", "#F14E1C", 0.5, refl=0.1)
M_BLUE = mat("blue", "#2F4F7C", 0.8)
M_SKYBLUE = mat("skyblue", "#5AA0E0", 0.5)
M_BAMBOO = mat("bamboo", "#C9A36B", 0.6)
M_BOTTLE = mat("bottle_glass", "#CFE4EA", 0.08, refl=0.7, alpha=0.38)
M_RUG = mat("rug", "#9A5038", 1.0)
M_FRAME = mat("frame", "#141416", 0.45, refl=0.1)
M_PR1 = mat("print_avatar", "#F4F1EB", 0.85, tex="print_avatar.png")
M_PR2 = mat("print_headline", "#F4F1EB", 0.85, tex="print_headline.jpg")
M_PLQ = mat("plaque", "#161413", 0.4, tex="plaque.jpg", refl=0.2)
M_AMBER = mat("amber", "#B9A65A", 0.4)
# emitters (drawn live in the page; here they only light the bake)
E_MAIN = mat("scr_main", emit="#9CC8FF", strength=5.0)
E_SIDE = mat("scr_side", emit="#9CC8FF", strength=5.0)
E_LAP = mat("scr_laptop", emit="#FFB070", strength=4.0, emit_tex="dusk_window.jpg")
E_BAR = mat("bar_glow", emit="#FFC98A", strength=30.0)
E_PC = mat("pc_glow", emit="#6A6CFF", strength=14.0)
E_PC2 = mat("pc_glow2", emit="#FF4FD8", strength=14.0)
E_SKY = mat("sky", emit="#FFFFFF", strength=2.2, emit_tex="dusk_window.jpg")
E_RING = mat("hp_ring", emit="#3DE0D0", strength=6.0)
E_LCD = mat("lcd", emit="#C9B96A", strength=1.5)

OBJ = []
def add(o):
    OBJ.append(o); return o

# ───────────────────────── room shell (lm 0) ─────────────────────────
X0, X1, Y0, ZC = -2.1, 2.3, -3.7, 2.7
WX0, WX1, WZ0, WZ1 = -1.92, -1.0, 0.95, 2.15   # window opening in the back wall
T = 0.12
def wall_piece(name, x0, x1, z0, z1):
    return add(B().box((x1 - x0, T, z1 - z0), ((x0 + x1) / 2, T / 2, (z0 + z1) / 2)).done(name, M_WALL, 0))
wall_piece("wall_back_l", X0, WX0, 0, ZC)
wall_piece("wall_back_r", WX1, X1, 0, ZC)
wall_piece("wall_back_t", WX0, WX1, WZ1, ZC)
wall_piece("wall_back_b", WX0, WX1, 0, WZ0)
add(B().box((T, -Y0, ZC), (X0 - T / 2, Y0 / 2, ZC / 2)).done("wall_left", M_WALL, 0))
add(B().box((T, -Y0, ZC), (X1 + T / 2, Y0 / 2, ZC / 2)).done("wall_right", M_WALL, 0))
add(B().box((X1 - X0, T, ZC), ((X0 + X1) / 2, Y0 - T / 2, ZC / 2)).done("wall_front", M_WALL, 0))
add(B().box((X1 - X0, -Y0, T), ((X0 + X1) / 2, Y0 / 2, ZC + T / 2)).done("ceiling", M_CEIL, 0))
add(B().box((X1 - X0, -Y0, T), ((X0 + X1) / 2, Y0 / 2, -T / 2)).done("floor", M_FLOOR, 0, uv=(0, 1, (1.6, 1.6))))
add(B().box((X1 - X0, 0.015, 0.09), ((X0 + X1) / 2, -0.0075, 0.045)).done("baseboard", M_TRIM, 0))
add(B().box((2.0, 1.5, 0.012), (0.0, -1.35, 0.006), bevel=0.004).done("rug", M_RUG, 0))
# window: frame, sill, mullions; the dusk view is a lit plane outside
wb = B()
wcx, wcz, ww, wh = (WX0 + WX1) / 2, (WZ0 + WZ1) / 2, WX1 - WX0, WZ1 - WZ0
for i, (sx, sz, lx, lz) in enumerate([(ww, 0.05, 0, wh / 2 - 0.025), (ww, 0.05, 0, -wh / 2 + 0.025), (0.05, wh - 0.1, -ww / 2 + 0.025, 0), (0.05, wh - 0.1, ww / 2 - 0.025, 0), (0.03, wh - 0.1, 0, 0), (ww - 0.1, 0.022, 0, 0.18)]):
    wb.box((sx, 0.06 - (0.012 if i == 5 else 0.0), sz), (wcx + lx, 0.06, wcz + lz))
wb.box((ww + 0.12, 0.16, 0.03), (wcx, -0.03, WZ0 - 0.015), bevel=0.006)
add(wb.done("win__frame", M_TRIM, 0))
add(B().plane(3.2, 2.0, (wcx - 0.1, 0.9, wcz + 0.1)).done("win__sky", E_SKY, -1))
def cull_outside(o):
    bm = bmesh.new(); bm.from_mesh(o.data)
    e = 1e-4
    kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        if c.x < X0 - e or c.x > X1 + e or c.y > T - e or c.y < Y0 - e or c.z > ZC + e or c.z < -e:
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bm.to_mesh(o.data); bm.free()
for o in list(OBJ):
    if o.name.startswith(("wall_", "ceiling", "floor")):
        cull_outside(o)
# wardrobe on the right
wd = B()
wd.box((0.98, 0.60, 2.28), (1.79, -0.30, 1.14), bevel=0.006)
add(wd.done("wardrobe", M_WALNUT, 0)); box_uv(OBJ[-1], (0.9, 1.8))
wd2 = B()
for dx in (-0.245, 0.245):
    wd2.box((0.46, 0.02, 2.06), (1.79 + dx, -0.612, 1.16), bevel=0.01)
add(wd2.done("wardrobe_doors", M_WALNUT, 0)); box_uv(OBJ[-1], (0.9, 1.8))
add(B().cyl(0.008, 0.16, (1.76, -0.632, 1.15), seg=12).cyl(0.008, 0.16, (1.82, -0.632, 1.15), seg=12).done("wardrobe_handles", M_SILVER, 0))

# ───────────────────────── desk set (lm 1) ─────────────────────────
DZ = 0.74
add(B().box((1.64, 0.72, 0.03), (0, -0.37, DZ - 0.015), bevel=0.004).done("desk__top", M_DESK, 1))
lg = B()
for sx in (-0.76, 0.76):
    lg.box((0.04, 0.60, DZ - 0.03), (sx, -0.37, (DZ - 0.03) / 2), bevel=0.004)
lg.box((1.48, 0.02, 0.30), (0, -0.08, 0.50))
add(lg.done("desk__legs", M_BLK, 1))
# birch riser under the monitors
RZ = DZ + 0.105
rs = B()
rs.box((1.16, 0.24, 0.018), (-0.045, -0.22, RZ - 0.009), bevel=0.003)
for sx in (-0.60, -0.045, 0.51):
    rs.box((0.018, 0.22, 0.087), (sx, -0.22, DZ + 0.0435))
add(rs.done("riser", M_BIRCH, 1, uv=(0, 1, (1.2, 0.3))))

def monitor(tag, cx, yaw, screen_mat):
    loc = (cx, -0.20, RZ); rot = (0, 0, R(yaw))
    b = B()
    b.box((0.542, 0.012, 0.318), (0, 0, 0.268), bevel=0.003)          # panel body
    b.box((0.30, 0.028, 0.16), (0, 0.016, 0.24), bevel=0.01)           # rear bulge
    b.box((0.542, 0.014, 0.018), (0, -0.001, 0.118), bevel=0.003)      # chin
    add(b.done(f"{tag}__body", M_BEZEL, 1, loc, rot))
    s = B()
    s.box((0.036, 0.012, 0.13), (0, 0.03, 0.075), bevel=0.003)
    s.box((0.20, 0.15, 0.007), (0, 0.01, 0.0035), bevel=0.003)
    add(s.done(f"{tag}__stand", M_SILVER, 1, loc, rot))
    add(B().plane(0.530, 0.298, (0, -0.0066, 0.274)).done(f"screen_{tag}", screen_mat, -1, loc, rot))
    # light bar
    lb = B()
    lb.cyl(0.011, 0.44, (0, -0.03, 0.452), rot=(0, R(90), 0), seg=16)
    lb.box((0.05, 0.05, 0.03), (0, 0.0, 0.44), bevel=0.004)
    add(lb.done(f"{tag}__bar", M_BLK, 1, loc, rot))
    add(B().box((0.40, 0.012, 0.002), (0, -0.03, 0.4405)).done(f"glow_bar_{tag}", E_BAR, -1, loc, rot))
    return loc, rot

monitor("main", -0.285, 5.0, E_MAIN)
monitor("side", 0.285, -5.0, E_SIDE)
add(B().box((0.075, 0.03, 0.028), (0, -0.215, RZ + 0.46), bevel=0.006).cyl(0.009, 0.006, (0, -0.232, RZ + 0.46), rot=(R(90), 0, 0), seg=14).done("webcam", M_BLK, 1))

# PC tower with glass front and two RGB fans
PCX, PCY = 0.715, -0.235
add(B().box((0.21, 0.39, 0.44), (PCX, PCY, DZ + 0.22), bevel=0.006).done("pc__case", M_BLK, 1))
add(B().box((0.19, 0.004, 0.42), (PCX, PCY - 0.197, DZ + 0.22)).done("pc__glass", M_GLASSY, 1))
def ring(cx, cy, cz, r, n=28):
    return [(cx + r * math.cos(i / n * 2 * math.pi), cy, cz + r * math.sin(i / n * 2 * math.pi)) for i in range(n)]
add(B().tube(ring(PCX, PCY - 0.2005, DZ + 0.32, 0.062), 0.006, 8, closed=True).done("glow_pc_a", E_PC, -1))
add(B().tube(ring(PCX, PCY - 0.2005, DZ + 0.13, 0.062), 0.006, 8, closed=True).done("glow_pc_b", E_PC2, -1))
fb = B()
for cz in (DZ + 0.32, DZ + 0.13):
    fb.cyl(0.018, 0.004, (PCX, PCY - 0.2, cz), rot=(R(90), 0, 0), seg=14)
    for k in range(7):
        a = k / 7 * 2 * math.pi
        fb.box((0.05, 0.002, 0.014), (PCX + 0.034 * math.cos(a), PCY - 0.2, cz + 0.034 * math.sin(a)), rot=(0, -a, 0))
add(fb.done("pc__fans", M_BLK2, 1))

# laptop, angled toward the seat
LP = (0.47, -0.565, DZ); LR = (0, 0, R(-20))
lb = B()
lb.box((0.34, 0.235, 0.014), (0, 0, 0.007), bevel=0.004)
lb.box((0.34, 0.008, 0.225), (0, 0.1175 + 0.03, 0.014 + 0.108), rot=(R(-15), 0, 0), bevel=0.003)
add(lb.done("laptop__body", M_GRAPH, 1, LP, LR))
kb = B().box((0.28, 0.105, 0.0015), (0, 0.025, 0.0148)).box((0.10, 0.06, 0.001), (0, -0.07, 0.0146))
add(kb.done("laptop__keys", M_BLK2, 1, LP, LR))
add(B().plane(0.318, 0.20, (0, 0.1175 + 0.0255, 0.014 + 0.108), rot=(R(-15), 0, 0)).done("screen_laptop", E_LAP, -1, LP, LR))

# desk mat, keyboard, mug, bottle
add(B().box((0.72, 0.32, 0.004), (-0.14, -0.53, DZ + 0.002), bevel=0.0015).done("deskmat", M_MAT, 1))
KX, KY = -0.14, -0.545
add(B().box((0.445, 0.142, 0.022), (KX, KY, DZ + 0.015), bevel=0.005).done("keyboard__base", M_BLK, 1))
kc = B(); ke = B()
rows = [(17, 0.0185), (15, 0.0185), (14, 0.0185), (13, 0.0185), (12, 0.0185)]
for ri, (n, w) in enumerate(rows):
    y = KY + 0.052 - ri * 0.0215
    total = 0.415
    cw = total / n
    for i in range(n):
        x = KX - total / 2 + cw * (i + 0.5)
        target = ke if (ri, i) in [(0, 0), (2, 13), (4, 11)] else kc
        target.box((cw - 0.004, 0.0175, 0.008), (x, y, DZ + 0.030), bevel=0.0018, seg=1)
kc.box((0.13, 0.0175, 0.008), (KX - 0.02, KY - 0.0545, DZ + 0.030), bevel=0.0018, seg=1)
for i, x in enumerate([-0.19, -0.16, -0.13, 0.07, 0.10, 0.13, 0.16, 0.19]):
    kc.box((0.026, 0.0175, 0.008), (KX + x, KY - 0.0545, DZ + 0.030), bevel=0.0018, seg=1)
add(kc.done("keyboard__keys", M_KEY, 1)); add(ke.done("keyboard__accent", M_KEYE, 1))
mg = B().cyl(0.04, 0.09, (-0.57, -0.47, DZ + 0.045), seg=28)
mg.tube([(-0.57 + 0.04 + 0.03 * math.sin(a), -0.47, DZ + 0.045 + 0.028 * math.cos(a)) for a in [i / 10 * math.pi for i in range(11)]], 0.006, 8)
add(mg.done("mug", M_EMBER, 1))
add(B().cyl(0.035, 0.004, (-0.57, -0.47, DZ + 0.088), seg=28).done("mug__coffee", mat("coffee", "#1C0F08", 0.2, refl=0.3), 1))
BX, BY = -0.70, -0.60
add(B().cyl(0.037, 0.135, (BX, BY, DZ + 0.0675), seg=28).done("bottle__sleeve", M_BLUE, 1))
add(B().cyl(0.035, 0.075, (BX, BY, DZ + 0.135 + 0.0375), seg=28, r2=0.030).done("bottle__glass", M_BOTTLE, 1))
add(B().cyl(0.026, 0.03, (BX, BY, DZ + 0.225), seg=24).done("bottle__lid", M_BAMBOO, 1))

# snake plant, left of the monitors
SX, SY = -0.715, -0.17
add(B().cyl(0.075, 0.10, (SX, SY, DZ + 0.05), seg=28, r2=0.085).done("snake__pot", M_POT, 1))
add(B().cyl(0.078, 0.004, (SX, SY, DZ + 0.097), seg=28).done("snake__soil", M_SOIL, 1))
rnd = np.random.default_rng(3)
sp = B()
for i in range(13):
    a = i / 13 * 2 * math.pi + rnd.random() * 0.5
    lean = 0.04 + rnd.random() * 0.30
    L = 0.22 + rnd.random() * 0.30
    rr = 0.015 + 0.035 * rnd.random()
    sp.leaf(L, 0.062 + rnd.random() * 0.02, (SX + rr * math.cos(a), SY + rr * math.sin(a), DZ + 0.09), (R(90) - lean, 0, a - R(90)), fold=0.22, bend=-0.05 + rnd.random() * 0.08, n=9, twist=(rnd.random() - 0.5) * 1.1)
add(sp.done("sway_snake", M_LEAF2, 1))
# small plant on the PC
add(B().cyl(0.04, 0.06, (PCX, PCY + 0.02, DZ + 0.47), seg=22, r2=0.047).done("pcplant__pot", M_POT, 1))
pp = B()
for i in range(17):
    a = i / 17 * 2 * math.pi + rnd.random() * 0.4
    tilt = 0.5 + rnd.random() * 0.7
    pp.leaf(0.07 + rnd.random() * 0.05, 0.036, (PCX, PCY + 0.02, DZ + 0.50), (tilt, 0, a), fold=0.15, bend=0.5, n=4)
add(pp.done("sway_pcplant", M_LEAF, 1))

# ───────────────────────── wall set (lm 2) ─────────────────────────
PGX, PGZ, PGW, PGH = -0.02, 1.74, 0.76, 0.56
PY = -0.032   # pegboard front face
add(B().box((PGW, 0.012, PGH), (PGX, PY + 0.006, PGZ), bevel=0.003).done("pegboard", M_PEG, 1, uv=(0, 2, (0.08, 0.08))))
st = B()
for sx in (-0.33, 0.33):
    for sz in (-0.23, 0.23):
        st.cyl(0.008, 0.02, (PGX + sx, -0.01, PGZ + sz), rot=(R(90), 0, 0), seg=10)
add(st.done("pegboard__standoffs", M_BLK, 1))
add(B().box((0.66, 0.022, 0.016), (PGX, PY - 0.075, PGZ + PGH / 2 + 0.03), bevel=0.003).box((0.02, 0.07, 0.01), (PGX - 0.25, PY - 0.035, PGZ + PGH / 2 + 0.034)).box((0.02, 0.07, 0.01), (PGX + 0.25, PY - 0.035, PGZ + PGH / 2 + 0.034)).done("pegbar", M_BLK, 1))
add(B().box((0.62, 0.014, 0.002), (PGX, PY - 0.075, PGZ + PGH / 2 + 0.021)).done("glow_bar_peg", E_BAR, -1))
def px(x): return PGX + x
# shelf with the film camera (top left)
add(B().box((0.24, 0.085, 0.006), (px(-0.235), PY - 0.0425, 1.925)).box((0.24, 0.004, 0.02), (px(-0.235), PY - 0.083, 1.932)).done("peg__shelf", M_BLK, 1))
cam = B()
cam.box((0.125, 0.045, 0.07), (px(-0.25), PY - 0.045, 1.965), bevel=0.005)
cam.box((0.045, 0.03, 0.014), (px(-0.275), PY - 0.045, 2.005), bevel=0.003)
cam.cyl(0.027, 0.03, (px(-0.235), PY - 0.08, 1.962), rot=(R(90), 0, 0), seg=24)
add(cam.done("camera__body", M_BLK, 1))
add(B().box((0.125, 0.046, 0.012), (px(-0.25), PY - 0.045, 1.996), bevel=0.002).cyl(0.02, 0.004, (px(-0.235), PY - 0.096, 1.962), rot=(R(90), 0, 0), seg=24).done("camera__trim", M_SILVER, 1))
add(B().tube([(px(-0.17 + 0.035 * math.cos(a)), PY - 0.03 - 0.02 * abs(math.sin(a)), 1.95 + 0.04 * math.sin(a)) for a in [i / 14 * 2 * math.pi for i in range(14)]], 0.003, 6, closed=True).done("camera__strap", M_BLK2, 1))
# book on two hooks
add(B().box((0.245, 0.018, 0.17), (px(-0.235), PY - 0.012, 1.745)).done("book__pages", M_PAGES, 1))
bk = B().plane(0.245, 0.17, (px(-0.235), PY - 0.0215, 1.745))
add(bk.done("book__cover", M_BOOK, 1))
add(B().box((0.012, 0.03, 0.02), (px(-0.31), PY - 0.015, 1.652)).box((0.012, 0.03, 0.02), (px(-0.16), PY - 0.015, 1.652)).done("book__hooks", M_BLK, 1))
# phone in a holder
add(B().box((0.072, 0.009, 0.15), (px(0.0), PY - 0.012, 1.745), bevel=0.004).done("phone__body", M_GLASSY, 1))
add(B().box((0.086, 0.03, 0.035), (px(0.0), PY - 0.015, 1.672), bevel=0.003).done("phone__holder", M_BLK, 1))
# mouse, cable coil, watch
add(B().sphere(0.05, (px(0.145), PY - 0.03, 1.925), scale=(0.66, 0.45, 1.15), seg=22).done("mouse__body", M_GRAPH, 1))
add(B().box((0.06, 0.03, 0.012), (px(0.145), PY - 0.015, 1.868)).done("mouse__hook", M_BLK, 1))
add(B().tube([(px(0.03 + 0.03 * math.cos(a) * (1 + 0.08 * math.sin(3 * a))), PY - 0.012 - 0.004 * math.cos(5 * a), 1.93 + 0.022 * math.sin(a)) for a in [i / 40 * 4 * math.pi for i in range(40)]], 0.0035, 6).done("cable", M_BLK2, 1))
wt = B()
wt.box((0.044, 0.014, 0.046), (px(0.185), PY - 0.012, 1.725), bevel=0.004)
wt.box((0.024, 0.006, 0.05), (px(0.185), PY - 0.008, 1.772)).box((0.024, 0.006, 0.05), (px(0.185), PY - 0.008, 1.678))
add(wt.done("watch__body", M_BLK, 1))
add(B().plane(0.03, 0.022, (px(0.185), PY - 0.0195, 1.727)).done("glow_watch", E_LCD, -1))
# headphones
def headphones(tag, cx, cz, ring_glow):
    r = 0.078
    arc = [(cx + r * math.cos(a), PY - 0.045, cz + r * math.sin(a)) for a in [R(-10) + i / 16 * R(200) for i in range(17)]]
    hb = B().tube(arc, 0.011, 8)
    for sx in (-1, 1):
        hb.cyl(0.043, 0.036, (cx + sx * (r + 0.004), PY - 0.045, cz - 0.03), rot=(0, R(90), 0), seg=22)
    add(hb.done(f"{tag}__band", M_BLK, 1))
    cu = B()
    for sx in (-1, 1):
        cu.cyl(0.046, 0.016, (cx + sx * (r - 0.02), PY - 0.045, cz - 0.03), rot=(0, R(90), 0), seg=22)
    add(cu.done(f"{tag}__pads", M_BLK2, 1))
    add(B().box((0.012, 0.05, 0.012), (cx, PY - 0.025, cz + r - 0.012)).done(f"{tag}__hook", M_BLK, 1))
    if ring_glow:
        rg = [(cx + r + 0.0235, PY - 0.045 + 0.03 * math.cos(a), cz - 0.03 + 0.03 * math.sin(a)) for a in [i / 20 * 2 * math.pi for i in range(20)]]
        add(B().tube(rg, 0.003, 6, closed=True).done("glow_hp", E_RING, -1))
headphones("hp1", px(0.285), 1.88, True)
headphones("hp2", px(0.285), 1.64, False)
# drawing tablet
add(B().box((0.25, 0.008, 0.16), (px(0.045), PY - 0.012, 1.555), bevel=0.004).done("tablet__body", M_TABLET, 1))
tb = B()
for i in range(6):
    tb.box((0.022, 0.002, 0.012), (px(0.145), PY - 0.017, 1.495 + i * 0.024), bevel=0.001, seg=1)
add(tb.done("tablet__keys", M_BLK2, 1))
add(B().box((0.03, 0.03, 0.012), (px(-0.04), PY - 0.015, 1.468)).box((0.03, 0.03, 0.012), (px(0.13), PY - 0.015, 1.468)).done("tablet__hooks", M_BLK, 1))
# pen tray with stylus, and a cup of pens
add(B().box((0.19, 0.06, 0.006), (px(-0.27), PY - 0.03, 1.487)).box((0.19, 0.004, 0.022), (px(-0.27), PY - 0.058, 1.498)).box((0.03, 0.03, 0.03), (px(-0.335), PY - 0.03, 1.505), bevel=0.004).done("tray", M_BLK, 1))
add(B().cyl(0.0045, 0.15, (px(-0.335), PY - 0.03, 1.59), seg=10, r2=0.003).done("stylus", M_BLK2, 1))
add(B().box((0.056, 0.05, 0.07), (px(-0.105), PY - 0.027, 1.512), bevel=0.004).done("pencup", M_BLK, 1))
add(B().cyl(0.0045, 0.12, (px(-0.115), PY - 0.03, 1.575), rot=(0, R(8), 0), seg=8).done("pen_a", M_SKYBLUE, 1))
add(B().cyl(0.0045, 0.11, (px(-0.098), PY - 0.022, 1.57), rot=(R(6), R(-9), 0), seg=8).done("pen_b", M_EMBER, 1))
add(B().cyl(0.0045, 0.10, (px(-0.09), PY - 0.035, 1.565), rot=(R(-5), R(-3), 0), seg=8).done("pen_c", M_POT, 1))

# hanging pothos beside the window
HX, HY, HZ = -0.72, -0.20, 1.93
add(B().cyl(0.082, 0.105, (HX, HY, HZ), seg=28, r2=0.07).done("hang__pot", M_POT, 1))
rp = B()
knot = (HX, HY, HZ + 0.42)
rp.tube([knot, (HX, HY, ZC)], 0.004, 6)
for k in range(4):
    a = k / 4 * 2 * math.pi + 0.5
    rim = (HX + 0.083 * math.cos(a), HY + 0.083 * math.sin(a), HZ + 0.05)
    low = (HX + 0.06 * math.cos(a), HY + 0.06 * math.sin(a), HZ - 0.06)
    rp.tube([knot, ((knot[0] + rim[0]) / 2, (knot[1] + rim[1]) / 2, (knot[2] + rim[2]) / 2 + 0.01), rim, low, (HX, HY, HZ - 0.085)], 0.0032, 6)
rp.sphere(0.012, knot, seg=10).sphere(0.012, (HX, HY, HZ - 0.085), seg=10)
add(rp.done("hang__rope", M_ROPE, 1))
hp = B(); hp2 = B(); stems = B()
for i in range(34):   # crown
    a = i / 34 * 2 * math.pi + rnd.random() * 0.3
    (hp if i % 3 else hp2).heart(0.062 + rnd.random() * 0.03, 0.056 + rnd.random() * 0.016, (HX + 0.045 * math.cos(a), HY + 0.045 * math.sin(a), HZ + 0.05 + rnd.random() * 0.02), (R(15) + rnd.random() * 0.8, 0, a - R(90)), bend=0.5)
for v in range(11):    # trailing vines
    a = R(120) + v / 11 * R(300)
    base = Vector((HX + 0.078 * math.cos(a), HY + 0.078 * math.sin(a), HZ + 0.05))
    L = 0.20 + rnd.random() * 0.40
    pts = []
    for sgm in range(11):
        u = sgm / 10
        pts.append(base + Vector((0.055 * math.cos(a) * math.sin(u * 2.2) + 0.014 * math.sin(u * 9 + v), 0.055 * math.sin(a) * math.sin(u * 2.2) + 0.01 * math.cos(u * 7 + v), 0.03 * math.sin(u * 3.1) - L * u * u)))
    stems.tube(pts, 0.0026, 5)
    for sgm in range(1, 11):
        pnt = pts[sgm]; side = 1 if sgm % 2 else -1
        (hp if (sgm + v) % 3 else hp2).heart(0.052 + rnd.random() * 0.03, 0.05 + rnd.random() * 0.016, pnt, (R(-70) + (rnd.random() - 0.5) * 0.6, (rnd.random() - 0.5) * 0.5, R(180) + side * R(38) + (rnd.random() - 0.5) * 0.9), bend=0.25)
add(stems.done("sway_hang_stems", M_STEM, 1))
add(hp.done("sway_hang", M_LEAF, 1))
add(hp2.done("sway_hang_b", M_LEAF3, 1))

# floating shelf with two prints and a small plant; plaque above it
SHX, SHZ = 0.84, 1.42
add(B().box((0.62, 0.15, 0.022), (SHX, -0.075, SHZ), bevel=0.004).done("shelf", M_BIRCH, 1, uv=(0, 1, (1.2, 0.3))))
def framed(tag, cx, m, w=0.235, h=0.31, tilt=7, yoff=-0.045):
    loc = (cx, yoff, SHZ + 0.011); rot = (R(-tilt), 0, 0)
    add(B().box((w + 0.03, 0.016, h + 0.03), (0, 0, (h + 0.03) / 2), bevel=0.003).done(f"{tag}__frame", M_FRAME, 1, loc, rot))
    add(B().plane(w, h, (0, -0.0085, (h + 0.03) / 2)).done(f"print_{tag}", m, 1, loc, rot))
framed("avatar", SHX - 0.15, M_PR1)
framed("headline", SHX + 0.115, M_PR2, yoff=-0.07)
add(B().cyl(0.034, 0.05, (SHX - 0.265, -0.105, SHZ + 0.036), seg=20, r2=0.04).done("succ__pot", M_POT, 1))
sc = B()
for i in range(12):
    a = i / 12 * 2 * math.pi
    sc.leaf(0.05, 0.03, (SHX - 0.265, -0.105, SHZ + 0.06), (R(35 + 30 * (i % 2)), 0, a), fold=0.3, bend=-0.2, n=3)
add(sc.done("sway_succ", M_LEAF, 1))
add(B().box((0.33, 0.014, 0.215), (SHX, -0.007, 1.945), bevel=0.003).done("plaque__frame", M_FRAME, 1))
add(B().plane(0.30, 0.1875, (SHX, -0.0145, 1.945)).done("plaque_face", M_PLQ, 1))

# ───────────────────────── lights ─────────────────────────
light("L_window", "W", (wcx, 0.02, wcz), (R(-90), 0, 0), (0.40, 0.50, 1.0), 150, (ww - 0.08, wh - 0.08), 160)
light("L_sunset", "W", (wcx + 0.1, 0.06, wcz - 0.25), (R(-100), 0, R(-18)), (1.0, 0.44, 0.22), 60, (0.7, 0.5), 120)
for tag, cx, yaw in (("main", -0.285, 5.0), ("side", 0.285, -5.0)):
    light(f"L_bar_{tag}", "P", (cx, -0.235, RZ + 0.437), (R(-20), 0, R(yaw)), (1.0, 0.70, 0.40), 22, (0.40, 0.012), 150)
light("L_bias", "P", (0.0, -0.12, RZ + 0.30), (R(-90), 0, 0), (1.0, 0.50, 0.20), 20, (1.05, 0.06), 170)
light("L_peg", "P", (PGX, PY - 0.075, PGZ + PGH / 2 + 0.018), (R(16), 0, 0), (1.0, 0.76, 0.50), 24, (0.62, 0.012), 160)
light("L_shelf", "P", (SHX, -0.16, 2.22), (R(14), 0, 0), (1.0, 0.76, 0.52), 9, (0.5, 0.02), 140)
light("L_fill", "P", (1.2, -3.2, 2.2), (R(62), 0, R(22)), (1.0, 0.70, 0.48), 9, (0.9, 0.9), 180)

world = bpy.data.worlds.new("w"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.014, 0.03, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0

# ───────────────────────── render settings ─────────────────────────
scene.render.engine = "CYCLES"
cy = scene.cycles
cy.device = "CPU"
cy.samples = SPP
cy.use_denoising = True
cy.max_bounces = 6; cy.diffuse_bounces = 4; cy.glossy_bounces = 2; cy.transmission_bounces = 4
cy.sample_clamp_indirect = 4.0
cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 1.0
cy.use_adaptive_sampling = False
scene.render.threads_mode = "AUTO"
try:
    cy.denoiser = "OPENIMAGEDENOISE"
except Exception as e:
    print("denoiser:", e)

EMIT_STATE = {"scr_main": "B", "scr_side": "B", "sky": "W"}   # every other emitter belongs to the lamps ("P")
def emission(m):
    return m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]

def set_state(state):
    """W = dusk from the window. P = lamps and small glows. B = the two monitors. ALL = everything."""
    for o in scene.objects:
        if o.type == "LIGHT":
            o.hide_render = state not in ("ALL", o["kind"])
    for m in bpy.data.materials:
        if "em" in m.keys() and m["em"] > 0:
            st = EMIT_STATE.get(m.name, "P")
            emission(m).default_value = m["em"] if state in ("ALL", st) else 0.0
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0 if state in ("ALL", "W") else 0.0

def add_camera(name, loc, target, lens_fov_v=36, pano=False):
    cd = bpy.data.cameras.new(name)
    o = bpy.data.objects.new(name, cd); col.objects.link(o)
    o.location = loc
    d = Vector(target) - Vector(loc)
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if pano:
        cd.type = "PANO"; cd.panorama_type = "EQUIRECTANGULAR"
    else:
        cd.sensor_fit = "VERTICAL"; cd.angle_y = R(lens_fov_v)
    return o

# ───────────────────────── stages ─────────────────────────
def stage_preview():
    set_state("ALL")
    scene.camera = add_camera("cam", (0.0, -2.55, 1.32), (0.0, 0.0, 1.28))
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = float(OPT.get("exp", 0.0))
    scene.render.filepath = os.path.join(RAW, f"preview_{OPT.get('tag', 'a')}.png")
    bpy.ops.render.render(write_still=True)

def lm_objects(g):
    return [o for o in OBJ if o.get("lm", -1) == g]

def unwrap(g):
    objs = lm_objects(g)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
        o.data.uv_layers.active = o.data.uv_layers["LM"]
    bpy.context.view_layer.objects.active = objs[0]
    scene.tool_settings.use_uv_select_sync = True
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=R(66), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(margin=0.003, rotate=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    print(f"[unwrap] group {g}: {len(objs)} objects")

def bake_group(g, state, res, spp):
    objs = lm_objects(g)
    img = bpy.data.images.new(f"lm{g}_{state}", res, res, alpha=False, float_buffer=True)
    img.colorspace_settings.name = "Non-Color"
    for o in objs:
        for m in o.data.materials:
            nt = m.node_tree
            n = nt.nodes.get("BAKE") or nt.nodes.new("ShaderNodeTexImage")
            n.name = "BAKE"; n.image = img
            nt.nodes.active = n
    set_state(state)
    cy.samples = spp
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
        o.data.uv_layers.active = o.data.uv_layers["LM"]
    bpy.context.view_layer.objects.active = objs[0]
    bk = scene.render.bake
    bk.use_pass_direct = True; bk.use_pass_indirect = True; bk.use_pass_color = False
    bk.margin = 6; bk.use_clear = True; bk.target = "IMAGE_TEXTURES"
    t = time.time()
    bpy.ops.object.bake(type="DIFFUSE")
    px = np.empty(res * res * 4, np.float32)
    img.pixels.foreach_get(px)
    np.save(os.path.join(RAW, f"lm{g}_{state}.npy"), px.reshape(res, res, 4)[::-1, :, :3].copy())
    print(f"[bake] group {g} state {state} {res}px {spp}spp: {time.time() - t:.1f}s  max={px.max():.2f}")
    bpy.data.images.remove(img)

def stage_bake():
    for g in [0, 1]:
        unwrap(g)
    for g in ONLY:
        for st in OPT.get("states", "W,P,B").split(","):
            if st == "B":
                bake_group(g, "B", max(1024, RES // 2), max(32, SPP // 2))
            else:
                bake_group(g, st, RES, SPP if st == "P" else max(32, SPP // 2))

def stage_env():
    set_state("ALL")
    scene.camera = add_camera("pano", (0.0, -0.95, 1.22), (0.0, 0.0, 1.22), pano=True)
    scene.camera.rotation_euler = (R(90), 0, 0)
    scene.render.resolution_x, scene.render.resolution_y = 1024, 512
    cy.samples = 48
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.exposure = -1.0
    scene.render.image_settings.file_format = "JPEG"; scene.render.image_settings.quality = 88
    scene.render.filepath = os.path.join(OUT, "env.jpg")
    bpy.ops.render.render(write_still=True)

def stage_export():
    for o in OBJ:
        for m in o.data.materials:
            n = m.node_tree.nodes.get("BAKE")
            if n:
                m.node_tree.nodes.remove(n)
    set_state("ALL")
    bpy.ops.object.select_all(action="DESELECT")
    for o in OBJ:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "studio.glb"), export_format="GLB", use_selection=True,
        export_extras=True, export_cameras=False, export_lights=False, export_apply=False, export_yup=True,
        export_texcoords=True, export_normals=True, export_materials="EXPORT", export_image_format="JPEG", export_jpeg_quality=86)
    print("[export] objects:", len(OBJ), "tris:", sum(len(o.data.polygons) for o in OBJ))

t0 = time.time()
if STAGE == "preview":
    stage_preview()
elif STAGE == "bake":
    stage_bake(); stage_export()
elif STAGE == "env":
    stage_env()
elif STAGE == "export":
    for g in [0, 1]:
        unwrap(g)
    stage_export()
elif STAGE == "all":
    stage_bake(); stage_export(); stage_env()
print(f"[done] {STAGE} in {time.time() - t0:.1f}s")
