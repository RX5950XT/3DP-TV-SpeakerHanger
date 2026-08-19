# -*- coding: utf-8 -*-
"""
電視壁掛架掛勾喇叭籃　參數化重建腳本
執行：  "C:\\Program Files\\FreeCAD 1.2\\bin\\FreeCADCmd.exe" build_basket.py

座標系：
  X  水平（電視左右），0 = 兩掛鉤中點，掛鉤在 X = ±HOOK_PITCH/2
  Y  深度，0 = 角鋼沖孔面（背板貼合面），+Y = 朝觀眾／電視方向
  Z  垂直，0 = 橢圓孔「下緣」（掛鉤承重點），+Z 向上
"""
import os
import sys
import FreeCAD
import Part

V = FreeCAD.Vector

# ══════════════════ 參數區（唯一需要動的地方）══════════════════
VERSION = "v3"

# ── 現場實測值（禁改）──
HOOK_PITCH = 200.0   # 兩橢圓孔中心間距
SLOT_W     = 8.3     # 橢圓孔寬
SLOT_H     = 19.8    # 橢圓孔高（長軸垂直）
GAP_TV     = 8.6     # 角鋼沖孔面 ↔ 電視背面
SPK_L, SPK_W, SPK_H = 200.0, 50.0, 70.0   # 喇叭 長 × 深 × 高

# ── 設計參數 ──
WALL    = 4.0    # 背板／側牆／前擋板厚（必須 < GAP_TV）
FLOOR   = 4.0    # 籃底厚
CLR_L   = 6.0    # 內腔長度總餘裕（喇叭左右各 3）
CLR_W   = 6.0    # 內腔深度總餘裕（喇叭前後各 3）
DROP    = 40.0   # ★調整旋鈕：掛鉤下延（孔下緣 → 籃口）。電視下緣位置變了就改這個
LIP_H   = 12.0   # ★調整旋鈕：前擋板高（籃底面起算）。要更防滑落就加大
TOP_EXT = 2.0    # 舌片上方背板延伸

# ── 背板減重鏤空（兩掛鉤之間直接開窗貫穿，上緣不封）──
#    上緣開放是刻意的：留橫樑就會有 160mm 長的橫向懸空邊，切片會在那裡多長一道支撐牆
#    載重全走掛鉤兩側的實心帶；窗下緣留一道橫帶把兩側綁回籃體
BP_KEEP_X   = 20.0  # ★調整旋鈕：自掛鉤中心往內保留的實心帶寬度。要更省就減
BP_KEEP_BOT = 6.0   # 窗下緣距籃口保留的實心橫帶高度

# ── 掛鉤 ──
TAB_W  = 7.4     # 穿孔舌片寬       （必須 < SLOT_W）
TAB_T  = 4.0     # 舌片厚（承重面）
HOOK_D = 12.0    # 下折長度         （TAB_T + HOOK_D 必須 < SLOT_H）
RAIL_T = 3.0     # 溝槽深＝可容納的角鋼板厚上限（實際約 1.5~2.0）
HOOK_T = 3.0     # 下折厚
CHAM   = 1.5     # 插入導引倒角
OVL    = 2.0     # 布林重疊量（避免面接觸造成多 Solid）

MATERIAL, DENSITY = "PETG", 1.27   # 報表用；PLA = 1.24

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ══════════════════ 推導尺寸 ══════════════════
CAV_L = SPK_L + CLR_L               # 206  內腔長
CAV_W = SPK_W + CLR_W               # 56   內腔深
CAV_H = SPK_H                       # 70   內腔高
OUT_W = CAV_L + 2 * WALL            # 214  總寬
OUT_D = CAV_W + 2 * WALL            # 64   總深
XH    = OUT_W / 2.0                 # 107
Z_TOP       = TAB_T + TOP_EXT       # +6   件頂
Z_CAV_TOP   = -DROP                 # -40  籃口
Z_FLOOR_TOP = Z_CAV_TOP - CAV_H     # -110 籃底面
Z_BOT       = Z_FLOOR_TOP - FLOOR   # -114 件底
Z_LIP_TOP   = Z_FLOOR_TOP + LIP_H   # -98  前擋板頂
REACH = RAIL_T + HOOK_T             # 6    角鋼面後方伸出量
BP_X  = HOOK_PITCH / 2.0 - BP_KEEP_X    # 80   窗半寬
BP_Z0 = Z_CAV_TOP + BP_KEEP_BOT         # -34  窗下緣（上緣直接開到件頂 Z_TOP）
E = 0.01

assert WALL < GAP_TV,           "背板厚超出電視餘隙"
assert TAB_W < SLOT_W - 0.5,    "舌片過寬，塞不進橢圓孔"
assert TAB_T + HOOK_D < SLOT_H, "插入高度超過孔高，勾不進去"
assert REACH < 0.5 * SLOT_H,    "後伸量過大"
assert BP_Z0 < Z_TOP,           "鏤空高度為負，BP_KEEP_BOT 太大"
assert BP_KEEP_BOT > 0,         "窗下緣要留實心橫帶把兩側綁回籃體"
assert BP_X + TAB_W / 2.0 < HOOK_PITCH / 2.0, "鏤空切到掛鉤根部"


def build():
    # 1) 籃體實心外框
    s = Part.makeBox(OUT_W, OUT_D, Z_CAV_TOP - Z_BOT, V(-XH, 0, Z_BOT))

    # 2) 挖內腔（上方開放）
    s = s.cut(Part.makeBox(CAV_L, CAV_W, (Z_CAV_TOP + 10) - Z_FLOOR_TOP,
                           V(-CAV_L / 2.0, WALL, Z_FLOOR_TOP)))

    # 3) 前開口（擋板以上、兩側牆之間全開）
    s = s.cut(Part.makeBox(CAV_L, WALL + E, (Z_CAV_TOP + 10) - Z_LIP_TOP,
                           V(-CAV_L / 2.0, OUT_D - WALL, Z_LIP_TOP)))

    # 4) 籃口以上背板（往下重疊 OVL 進籃體背牆 → 體積重疊，確保單一 Solid）
    s = s.fuse(Part.makeBox(OUT_W, WALL, Z_TOP - (Z_CAV_TOP - OVL),
                            V(-XH, 0, Z_CAV_TOP - OVL)))

    # 5) 掛鉤（YZ 剖面多邊形沿 X 擠出）
    #    剖面：舌片(Z 0~TAB_T, Y -REACH~WALL) + 下折(Z -HOOK_D~0, Y -REACH~-RAIL_T)
    #    兩者之間 Y -RAIL_T~0 為空槽，角鋼板由下方滑入
    for xc in (+HOOK_PITCH / 2.0, -HOOK_PITCH / 2.0):
        prof = [(WALL,            TAB_T),
                (-REACH + CHAM,   TAB_T),
                (-REACH,          TAB_T - CHAM),
                (-REACH,         -HOOK_D + CHAM),
                (-REACH + CHAM,  -HOOK_D),
                (-RAIL_T,        -HOOK_D),
                (-RAIL_T,         0.0),
                (WALL,            0.0)]
        x0 = xc - TAB_W / 2.0
        pts = [V(x0, y, z) for (y, z) in prof]
        face = Part.Face(Part.makePolygon(pts + [pts[0]]))
        s = s.fuse(face.extrude(V(TAB_W, 0, 0)))

    # 6) 背板減重鏤空（最後才切，符合「先 fuse 特徵、後 cut 孔」）
    #    Y 切穿整片背板；Z 切超過件頂 → 上緣開放，沒有橫樑就沒有懸空邊
    s = s.cut(Part.makeBox(2 * BP_X, WALL + 2 * E, (Z_TOP + E) - BP_Z0,
                           V(-BP_X, -E, BP_Z0)))

    try:
        s = s.removeSplitter()
    except Exception as exc:
        print("removeSplitter skipped:", exc)
    return s


def report(shape):
    """量測並輸出驗證報表。FreeCADCmd 會吞掉 stdout，故同時寫檔。"""
    bb = shape.BoundBox
    ok = (len(shape.Solids) == 1 and shape.isValid() and shape.isClosed()
          and abs(bb.XLength - OUT_W) < 0.01
          and abs(bb.ZLength - (Z_TOP - Z_BOT)) < 0.01
          and abs(bb.YLength - (OUT_D + REACH)) < 0.01)
    lines = [
        "=" * 62,
        "TV_Speaker_Basket %s" % VERSION,
        "=" * 62,
        "BoundBox  X=%.2f [%.1f,%.1f]  (預期 %.1f)" % (bb.XLength, bb.XMin, bb.XMax, OUT_W),
        "          Y=%.2f [%.1f,%.1f]  (預期 %.1f = 籃深%.0f + 勾後伸%.0f)"
        % (bb.YLength, bb.YMin, bb.YMax, OUT_D + REACH, OUT_D, REACH),
        "          Z=%.2f [%.1f,%.1f]  (預期 %.1f)"
        % (bb.ZLength, bb.ZMin, bb.ZMax, Z_TOP - Z_BOT),
        "Solids=%d (預期 1)  Faces=%d  Edges=%d"
        % (len(shape.Solids), len(shape.Faces), len(shape.Edges)),
        "isValid=%s  isClosed=%s" % (shape.isValid(), shape.isClosed()),
        "Volume=%.1f mm3  (100%% 實心約 %.0f g %s；實際切片會少約一半)"
        % (shape.Volume, shape.Volume / 1000.0 * DENSITY, MATERIAL),
        "-" * 62,
        "插入檢查  舌片寬 %.1f < 孔寬 %.1f       -> %s" % (TAB_W, SLOT_W, "OK"),
        "插入檢查  舌厚+下折 %.1f < 孔高 %.1f    -> %s" % (TAB_T + HOOK_D, SLOT_H, "OK"),
        "干涉檢查  背板厚 %.1f < 電視餘隙 %.1f   -> %s" % (WALL, GAP_TV, "OK"),
        "減重鏤空  %.0f(寬) x %.0f(高) 貫穿背板 %.1f  上緣開放無懸空  省 %.0f mm3"
        % (2 * BP_X, Z_TOP - BP_Z0, WALL, 2 * BP_X * (Z_TOP - BP_Z0) * WALL),
        "掛鉤兩側實心帶  %.0f mm 寬 x %.1f 厚 x2  (剪力面積 %.0f mm2)"
        % (BP_KEEP_X + OUT_W / 2.0 - HOOK_PITCH / 2.0, WALL,
           2 * (BP_KEEP_X + OUT_W / 2.0 - HOOK_PITCH / 2.0) * WALL),
        "=" * 62,
        "VERIFY: %s" % ("PASS" if ok else "FAIL"),
    ]
    txt = "\n".join(lines)
    print(txt)
    with open(os.path.join(OUT_DIR, "verify_%s.txt" % VERSION), "w", encoding="utf-8") as f:
        f.write(txt + "\n")
    return ok


shape = build()

fcstd = os.path.join(OUT_DIR, "TV_Speaker_Basket.FCStd")
doc = FreeCAD.newDocument("TV_Speaker_Basket")
obj = doc.addObject("Part::Feature", "Basket")
obj.Shape = shape
doc.recompute()
doc.saveAs(fcstd)

stl = os.path.join(OUT_DIR, "TV_Speaker_Basket_%s.stl" % VERSION)
obj.Shape.exportStl(stl)

print("FCStd :", fcstd)
print("STL   :", stl)
report(obj.Shape)   # 不要用 sys.exit()，FreeCADCmd 會回報 "unexpectedly terminated"
