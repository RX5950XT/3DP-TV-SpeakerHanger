# CLAUDE.md — 專案規範

電視壁掛架掛勾喇叭籃（FreeCAD 參數化 CSG 建模 → FDM 3D 列印）。
交接（現況、設計理由、切片參數、待辦）見 `tasks/todo.md`（保持 ≤100 行）；對外說明見 `README.md`。
本檔只寫本專案特有規範，通用工作原則見 `~/.claude/CLAUDE.md`。

## 禁止事項

1. **路徑一律 ASCII**：專案路徑、腳本路徑、輸出路徑全程不得含中文。
   含中文時 FreeCADCmd 直接回 `Application unexpectedly terminated`，
   沒有 traceback、什麼都不產生，極難察覺。
2. **腳本內不得使用 `sys.exit()`**：FreeCADCmd 會當成異常終止。
   驗證結果一律寫檔（`cad/verify_<版本>.txt`），不靠 stdout。
3. **不得覆蓋 STL**：每次幾何變更 → `VERSION` +1 → 產生新 `*_v<n>.stl`，舊版保留。
   FCStd 維持單一工作檔 `cad/TV_Speaker_Basket.FCStd`。
4. **不得手改 FCStd／STL**：`cad/build_basket.py` 是唯一真相來源，
   所有幾何變更都改參數後重跑腳本。
5. **不得修改實測值**：`HOOK_PITCH` / `SLOT_W` / `SLOT_H` / `GAP_TV` /
   `SPK_L,W,H` 是現場量的，只有使用者能改。
6. **不得覆蓋使用者既有的 Bambu Studio 預設**，只新增。新增前確認
   `BambuStudio.conf` 的 `sync_user_preset = false`，否則啟動時雲端同步會刪掉本地預設。
7. **背板鏤空的上緣不得封起來**。封了就多一道 160mm 長的水平懸空邊，切片會長一整片支撐。
   這是 v2→v3 特意改掉的，別「順手補回去」。

## 關鍵尺寸（實測，禁改）

| 項目 | 值 |
|------|-----|
| 兩橢圓孔中心間距 | 200 mm |
| 橢圓孔 | 寬 8.3 × 高 19.8 mm（長軸垂直） |
| 角鋼沖孔面 ↔ 電視背面 | 8.6 mm（懸掛結構厚度上限） |
| 喇叭 | 長 200 × 深 50 × 高 70 mm |

## 座標系

- **X** 水平（電視左右），0 = 兩掛鉤中點，掛鉤在 X = ±100
- **Y** 深度，0 = 角鋼沖孔面（背板貼合面），+Y = 朝觀眾／電視方向
- **Z** 垂直，0 = 橢圓孔下緣（掛鉤承重點），+Z 向上

## 建模流程（每次幾何變更都要跑完）

```powershell
# 1) 改 cad\build_basket.py 參數區（含 VERSION +1）
# 2) 建模
& "C:\Program Files\FreeCAD 1.2\bin\FreeCADCmd.exe" `
  "D:\Workspace\Personal_Project\3DP-TV-SpeakerHanger\cad\build_basket.py"
# 3) 讀驗證報表（stdout 會亂碼，一律讀檔）
Get-Content cad\verify_v<n>.txt
# 4) 出目視驗證圖
python cad\render_views.py v<n>
# 5) 更新 tasks/todo.md 現況（≤100 行，只留結論）
```

## 驗收標準（全過才算完成）

- `verify_*.txt` 顯示 `VERIFY: PASS`
- `Solids=1`、`isValid=True`、`isClosed=True`
- BoundBox 與參數推導值誤差 < 0.01mm
- 6 張 `cad/screenshots/v<n>_*.png` 目視無異常
- 朝下面清單裡的 ★需支撐 只有兩個下折勾底面（Z=−12，共 22.2 mm²），多出別的就是改壞了
- `tasks/todo.md` 現況已更新為當次結果

## CSG 建模守則

- 外伸特徵先 `fuse` 再 `cut` 孔；特徵根部要插入母體 1~3mm 造成體積重疊，
  只有面接觸會產生孤立 Solid（本專案用 `OVL=2.0`）。
- 布林完收尾 `removeSplitter()`，用 `try` 包住。
- 剖面能一次擠出成形就別用多個 box 疊布林（掛鉤即是，Faces 只有 32）。

## 列印規範

- **切片預設**：Bambu Studio 使用者預設 `TV喇叭籃 0.20 支撐`
  （A1 0.4 噴頭 / PETG Basic，繼承 `0.20mm Standard @BBL A1`）。逐項理由見 `tasks/todo.md` 切片參數。
- **`enable_support` 必開**：兩個下折勾底面在 Z=−12，是離平台 102mm 的完全懸空孤島，
  不支撐印不出來。用 `tree(auto)`，grid 柱在這個高度會被撞倒。
  這是全模型唯一的真懸空（22.2 mm²）；改幾何後用
  `python cad
ender_views.py v<n>` 的朝下面清單複查，多出別的 ★需支撐 就是改壞了。
- **列印方向：籃底朝下直立**（＝懸掛姿態），切片時不要旋轉。底面 214×64 實心平面附著佳、
  牆體全垂直零懸空。
- 平躺背板列印已否決：下折勾突出背面 6mm 會讓整片背板架空。
- 功能配合不可靠列印公差自然變緊，干涉要設計進幾何；
  凸出/凹陷特徵 < 0.5mm 印不出來。
