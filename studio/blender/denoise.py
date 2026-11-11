"""OIDN-denoise raw lightmap bakes through Blender's compositor. Run: blender -b -P denoise.py -- name1 name2 ...
Reads raw/<name>.npy (H, W, 3 float32, row 0 = top), writes raw/<name>_dn.npy."""
import bpy, sys, os, numpy as np
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
names = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam
sc.render.engine = "CYCLES"; sc.cycles.samples = 1; sc.cycles.device = "CPU"
tree = bpy.data.node_groups.new("den", "CompositorNodeTree")
tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
out = tree.nodes.new("NodeGroupOutput"); src = tree.nodes.new("CompositorNodeImage"); dn = tree.nodes.new("CompositorNodeDenoise")
print("denoise inputs:", [i.name for i in dn.inputs])
tree.links.new(src.outputs[0], dn.inputs[0]); tree.links.new(dn.outputs[0], out.inputs[0])
sc.compositing_node_group = tree
sc.render.use_compositing = True
sc.render.image_settings.file_format = "OPEN_EXR"; sc.render.image_settings.color_depth = "32"
sc.view_settings.view_transform = "Raw" if "Raw" in [v.name for v in type(sc.view_settings).bl_rna.properties["view_transform"].enum_items] else "Standard"
for n in names:
    a = np.load(os.path.join(RAW, n + ".npy")); h, w, _ = a.shape
    # dilate islands into the empty texels so the denoiser does not pull black across seams
    filled = a.copy(); mask = a.sum(axis=2) > 0
    for _ in range(12):
        nb = np.zeros_like(filled); cnt = np.zeros((h, w, 1), np.float32)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            s = np.roll(filled, (dy, dx), (0, 1)); m = np.roll(mask, (dy, dx), (0, 1))[..., None]
            nb += s * m; cnt += m
        grow = (~mask) & (cnt[..., 0] > 0)
        filled[grow] = (nb / np.maximum(cnt, 1))[grow]; mask = mask | grow
    img = bpy.data.images.new(n, w, h, alpha=False, float_buffer=True); img.colorspace_settings.name = "Non-Color"
    px = np.ones((h, w, 4), np.float32); px[..., :3] = filled[::-1]
    img.pixels.foreach_set(px.ravel()); src.image = img
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
    sc.render.filepath = os.path.join(RAW, n + "_dn.exr")
    bpy.ops.render.render(write_still=True)
    res = bpy.data.images.load(sc.render.filepath); res.colorspace_settings.name = "Non-Color"
    o = np.empty(w * h * 4, np.float32); res.pixels.foreach_get(o)
    o = o.reshape(h, w, 4)[::-1, :, :3].copy()
    np.save(os.path.join(RAW, n + "_dn.npy"), o)
    print(f"[denoise] {n}: in mean {a.mean():.4f} out mean {o.mean():.4f} max {o.max():.2f}")
    bpy.data.images.remove(img); bpy.data.images.remove(res); os.remove(sc.render.filepath)
