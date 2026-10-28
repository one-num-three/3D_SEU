# 校园底图 v0.4：轻快配色增量

这是 **建筑模型 v0.3 + 底图 v0.4**，不是重建了楼高的新建筑版。原 v01/v02/v03 文件保持不变。

## 内容
- `assets/SEU_basemap_overlay_v04.glb`：107 个独立面（106 个原 OSM 地表面 + 1 校园中性地面）；与 v03 使用相同米制原点，直接叠加，无缩放。
- `assets/SEU_basemap_overlay_v04.blend`：可编辑底图源，不含重复楼模。
- `data/BASEMAP_LAYERS.local.json`：实际输入数据，保留源 ID、标签、坐标、多边形内洞及三角化。
- `data/DISPLAY_STYLE.json`：建筑浅暖灰、绿地浅绿、湖水蓝、道路米白；近似候选保留低饱和橙。建筑展示材质按原材质亮度分组，保持窗/屋顶/墙面区别，不是重新判断建筑用途。
- `previews/`：原楼模叠新底图的真实 Blender 渲染；无高度夸张。北箭头是投影网格北，比例尺使用模型米。

## 不变与限制
所有 2726 个原建筑/道路/基底网格均保持原顶点、摆位、比例和高度。仅增加独立底图，网站按配置切换显示材质。浅橙 C3、兰园仍为近似候选，不标为已精确配准。楼高仍大量来自估计；101 处0.35米残余/通道标记不是真实矮楼。

地表为 61 片绿地、39 片运动场、4 片历史施工用地、2 片水面；仅采用已有 OSM 快照，不凭空补位置。不确定区域保持中性；施工状态不保证为当日状态；无地形测量。

旧校园边界顶面 Z=-0.01m；新地表Z=-0.008至-0.003m，处在原边界上、原道路最低+0.005m下。这些毫米差只用于图层排序，不是地理高程。网页应动态调整 near/far 防止深度闪烁，而不移动建筑或拉高地面。

## 复建 / 验证
仓库保留 `public_assets_v03` 和 `public_assets_v02` 作为固定依赖。
```sh
blender -b --python public_assets_v04/scripts/build_overlay.py
python3 public_assets_v04/scripts/validate_release.py
blender -b --python public_assets_v04/scripts/render_preview.py -- public_assets_v03/assets/SEU_campus_restored_v03.blend
```
首次导出需 Blender glTF 插件（Blender 标准发行附带）。预览脚本只在内存中切换显示材质，不保存/覆盖楼模。重建产生文件后manifest旧hash可能需更新，原发布检查只检冻结成品。

## 许可
地理数据库与可提取地理数据 ODbL 1.0，© OpenStreetMap contributors；自制配色/表现 CC BY 4.0（3D_SEU contributors）；代码 MIT。详见 `SOURCES_AND_RIGHTS.json` 和 `licenses/`。并非整包统一 MIT，也不重新授权第三方建筑设计。
