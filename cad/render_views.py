# -*- coding: utf-8 -*-
"""讀 STL 出圖：3 張正投影三視圖 + 2 張局部放大 + 1 張立體圖。
CLI 無 GUI（FreeCADCmd 不能截圖）時的目視驗證方案。

執行：  python cad/render_views.py [版本號，預設 v1]

座標系：X 左右、Y 深度（0 = 角鋼面，+Y 朝觀眾）、Z 垂直（0 = 橢圓孔下緣）。
三視圖用 2D 正投影（matplotlib 會自動裁切，可放大局部）；立體圖用 mplot3d。
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v1"

# name: (投影軸對, 橫軸標籤, 縱軸標籤, xlim, ylim)　lim=None 表示全模型
ORTHO_VIEWS = {
    "front":       ((0, 2), "X (mm)", "Z (mm)", None, None),
    "right":       ((1, 2), "Y (mm)", "Z (mm)", None, None),
    "top":         ((0, 1), "X (mm)", "Y (mm)", None, None),
    "hook_detail": ((1, 2), "Y (mm)", "Z (mm)", (-9, 9), (-18, 10)),
    "lip_detail":  ((1, 2), "Y (mm)", "Z (mm)", (-3, 70), (-118, -92)),
}


def load_stl(path):
    """STL（ASCII 或 binary 自動判別）→ (n_tri, 3, 3) 頂點陣列。"""
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:5] == b"solid" and b"facet" in raw[:512]:   # ASCII
        verts = [[float(v) for v in ln.split()[1:4]]
                 for ln in raw.decode("ascii", "replace").splitlines()
                 if ln.lstrip().startswith("vertex")]
        return np.asarray(verts, dtype=float).reshape(-1, 3, 3)
    n = int(np.frombuffer(raw[80:84], "<u4")[0])        # binary
    dt = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    return np.frombuffer(raw[84:84 + n * dt.itemsize], dtype=dt, count=n)["v"].astype(float)


def render_ortho(tris, name, axes, xlab, ylab, xlim, ylim, out):
    i, j = axes
    fig, ax = plt.subplots(figsize=(9, 7), dpi=140)
    ax.add_collection(PolyCollection(
        tris[:, :, [i, j]], facecolor="#7ba7d7", edgecolor="#16263c",
        linewidths=0.6, alpha=0.30))
    lo, hi = tris[:, :, [i, j]].reshape(-1, 2).min(0), tris[:, :, [i, j]].reshape(-1, 2).max(0)
    ax.set_xlim(xlim or (lo[0] - 4, hi[0] + 4))
    ax.set_ylim(ylim or (lo[1] - 4, hi[1] + 4))
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3, alpha=0.6)
    ax.set_xlabel(xlab); ax.set_ylabel(ylab)
    ax.set_title("%s  %s  (ortho)" % (VERSION, name))
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("saved", out)


def render_iso(tris, out):
    fig = plt.figure(figsize=(8, 8), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_proj_type("ortho")
    ax.add_collection3d(Poly3DCollection(
        tris, facecolor="#8fb3d9", edgecolor="#22314a", linewidths=0.35))
    lo, hi = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(hi - lo)
    ax.view_init(elev=22, azim=45)      # 相機在 +X+Y 象限 → 看得到開放的上方與前方
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.set_title("%s  iso" % VERSION)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("saved", out)


def overhang_report(tris, cos_limit=0.7):
    """列出朝下的面 = 切片時會長支撐的候選。cos_limit 0.7 ≈ 傾角 45° 以上。"""
    v = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    mag = np.maximum(np.linalg.norm(v, axis=1), 1e-12)
    area, nz = mag / 2.0, v[:, 2] / mag
    m = nz < -cos_limit
    print("\n朝下面（需支撐候選，nz < %.2f）：" % -cos_limit)
    if not m.any():
        print("  無")
        return
    cen = tris[m].mean(axis=1)
    z_bed = tris.reshape(-1, 3)[:, 2].min()
    need = 0.0
    for z, a, k, x, y in sorted(zip(cen[:, 2], area[m], nz[m], cen[:, 0], cen[:, 1])):
        if abs(z - z_bed) < 1e-6:
            tag = "貼平台，非懸空"
        elif k > -0.75:
            tag = "約 45 度，可自撐"
        else:
            tag = "★需支撐"
            need += a
        print("  Z=%8.2f  面積 %7.2f mm2  nz=%5.2f  中心 (X=%6.1f, Y=%5.1f)  %s"
              % (z, a, k, x, y, tag))
    print("  真正需要支撐的面積合計 %.1f mm2" % need)


def main():
    tris = load_stl(os.path.join(HERE, "TV_Speaker_Basket_%s.stl" % VERSION))
    print("triangles:", len(tris))
    overhang_report(tris)
    shots = os.path.join(HERE, "screenshots")
    os.makedirs(shots, exist_ok=True)
    render_iso(tris, os.path.join(shots, "%s_iso.png" % VERSION))
    for name, (axes, xlab, ylab, xlim, ylim) in ORTHO_VIEWS.items():
        render_ortho(tris, name, axes, xlab, ylab, xlim, ylim,
                     os.path.join(shots, "%s_%s.png" % (VERSION, name)))


if __name__ == "__main__":
    main()
