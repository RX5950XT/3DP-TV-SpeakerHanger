# 3DP-TV-SpeakerHanger todo
最後更新：2026-11-19

專案規範、實測尺寸、座標系、建模流程與驗收標準見 `CLAUDE.md`；對外說明見 `README.md`。

## 現況（交接）
- v3 建模完成並驗證通過（`cad/TV_Speaker_Basket_v3.stl`，VERIFY PASS、Solids=1、172 822.7 mm³ ≈ 219 g PETG 實心），切片預設已寫入 Bambu Studio，**尚未實際列印**。倉庫只保留 v3 產物。
- 版本演進：v1 實心背板 → v2 背板盲孔凹槽（作廢：凹槽頂緣是 160×2.8 mm 水平朝下面，會長整道支撐）→ v3 背板貫穿鏤空、上緣不封。
- 主要尺寸：內腔 206×56×70、外形 214×64×120（Z +6 ~ −114）、BoundBox 214×70×120；籃口 Z −40、籃底面 Z −110；前擋板高 12 頂在 Z −98；背板鏤空 X ±80、Z −34 以上開放；壁厚皆 4.0 mm。
- 照片判讀已完成不必重做：角鋼是垂直沖孔立柱、孔距約 30 mm 一格；喇叭前面幾乎整片網罩，所以前擋板必須淺。參考照片不在倉庫內。

### 設計決策（別推翻）
1. 掛鉤：舌片穿孔後下折的 L 形勾。舌片寬 7.4（< 孔寬 8.3）、厚 4、下折 12 → 插入高 16 < 孔高 19.8；舌片與下折間留 3.0 mm 槽容納角鋼板（實際約 1.5~2.0）。
2. 抗前傾：背板貼角鋼面（Y=0）形成力偶；1 mm 餘隙 ÷ 108 mm 力臂 → 傾角 0.5°，**不需要收緊**。
3. 列印方向：籃底朝下直立（＝懸掛姿態）。平躺背板列印已否決（下折勾突出 6 mm 會讓背板架空）。
4. 背板鏤空成 U 形：兩根 27 mm × 4 mm 實心帶各扛一個掛鉤，窗下緣 6 mm 橫帶（Z −40~−34）綁回籃體。承重約 9.1 N → 0.04 MPa，PETG 三個數量級餘裕。
5. 下折勾底面（Z −12，22.2 mm²）的支撐避不掉：勾外腿正下方（Y<0）全空；加斜撐會落在 Y −3~0，正是角鋼立柱本體位置。
6. 懸空稽核（v3）：真需支撐只有 22.2 mm²；Z 0 的 44.4 mm² 是舌片跨 3 mm 槽的短橋接；45° 倒角可自撐。
7. 省料的大頭是切片參數不是 CAD：`wall_loops` 3→2 一個參數就抵過 CAD 鏤空的 12.9%。

### 切片參數
預設 `TV喇叭籃 0.20 支撐`，繼承 `0.20mm Standard @BBL A1`（A1 0.4 噴頭、Bambu PETG Basic）。檔案不在倉庫，在 `%APPDATA%\BambuStudio\user\<user_id>\process\TV喇叭籃 0.20 支撐.json + .info`；`<user_id>` 從 `BambuStudio.conf` 的 `app.preset_folder` 讀。

| 參數 | 值 | 為什麼 |
|------|-----|--------|
| `enable_support` | 1 | 必開，兩個下折勾底面是離平台 102 mm 的孤島 |
| `support_type` | tree(auto) | 樹狀會靠著背板穩住；grid 柱在 102 mm 高會被撞倒 |
| `support_on_build_plate_only` | 1 | 籃內沒有懸空，不讓支撐長進去 |
| `support_top_z_distance` / `support_object_xy_distance` | 0.2 / 0.35 | PETG 黏支撐，要留間距才好剝 |
| `wall_generator` | arachne | 窄處要變寬度牆才填得滿 |
| `wall_loops` | 3 | 省料旋鈕：3 圈 ≈ 72% 實心；2 圈 ≈ 48%，但掛鉤變薄 |
| `sparse_infill_density` | 12% gyroid | 牆已佔大部分厚度 |
| `layer_height` | 0.20 | 4.0／12／3.0 都能被 0.2 整除 |
| `brim_type` / `brim_width` | outer_only / 5 | 長件、重心偏上，便宜保險 |
| `outer_wall_speed` / `bridge_speed` | 60 / 30 | PETG 外牆放慢；舌片短橋接 |

### 調整旋鈕
改需求時只動 `cad/build_basket.py` 參數區（開頭 7 個 `assert` 會擋違規參數）。

| 參數 | 預設 | 什麼時候改 |
|------|------|-----------|
| `DROP` | 40.0 | 籃子撞到電視下緣或想掛更低 → 加大（角鋼 30 mm 一格，換孔也能調） |
| `LIP_H` | 12.0 | 喇叭會滑出 → 加大；擋網罩太多 → 減小 |
| `CLR_L` / `CLR_W` | 6.0 / 6.0 | 喇叭放不進去 → 加大 |
| `RAIL_T` | 3.0 | 角鋼板比 3 mm 厚 → 加大；不要為了更貼而收緊 |
| `TAB_W` | 7.4 | 舌片塞不進孔 → 減小（上限 `SLOT_W` − 0.5）；不要加大 |
| `WALL` / `FLOOR` | 4.0 / 4.0 | 想更省料 → 3.0（實測 −26%、181 g、仍 VERIFY PASS），**等使用者決定** |
| `BP_KEEP_X` | 20.0 | 掛鉤兩側實心帶寬度；唯一載重路徑，別減太多 |
| `BP_KEEP_BOT` | 6.0 | 窗下緣橫帶高度，不要歸零 |

### 已知地雷（`CLAUDE.md` 未列的）
- FreeCAD MCP 的 GUI dispatch 間歇卡死 90 s：GUI 的 Measure 工具啟用中就會擋住，`FreeCADGui.Control.closeDialog()` + `resetEdit()` 可解。`view.setViewDirection()` 必定 timeout，改用 `get_view` 固定視角或 `viewIsometric()`；`reload_document`、`get_view` 較穩。
- Bambu Studio CLI 在 GUI 已開啟時無法用：`--slice` 交給既有實例，不產 gcode、不回 exit code，只在 cwd 丟一個沒切的 `result.json`。要用 CLI 先完全關閉 Studio。
- FreeCAD `exportStl()` 輸出 ASCII STL；mplot3d 不裁切 Poly3DCollection，局部放大要用 2D 正投影（`PolyCollection`）。

## 待辦
- [ ] 重啟 Bambu Studio 讓 `TV喇叭籃 0.20 支撐` 出現在 Process 選單（寫入時 Studio 正在執行）。
- [ ] 切片 v3，確認支撐只長在兩個下折勾底下，記錄實際克數與時間。
- [ ] 實際列印驗證；印後量掛鉤舌片與孔的配合，必要時調 `TAB_W`／`RAIL_T`。

## 需使用者決定
- `WALL`/`FLOOR` 是否降到 3.0。
- 是否加 LICENSE：公開倉庫目前沒有授權檔（＝保留所有權利）；README 原寫 MIT 但未經同意已拿掉。
