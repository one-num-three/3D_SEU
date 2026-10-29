# 全校原道路微表面显示候选 A

保持 398 原道路所有位置、面、孔洞、桥/层、宽度、旧调色与深度pass，不新加道路或降低几何精度。只为原面新增米制 world UV 和程序纹理。

只有 OSM 1223674537 明示 wood、1315044899 明示 paving_stones；这两条分别有原创木纹/铺装缝。木纹方向、铺块 0.6m 模数没有测量证据，是显示近似。其余 396 条全部标 inferred_display_only，沿旧 7 类颜色，仅乘极细中性颗粒，不凭空加砖缝、不声称实际沥青/石材；没有实拍贴图。桥也不改高度、栏杆、走向或孔洞。

在 generic ground 配置之后调用 applyRoadMicroSurfaces(THREE, campusRoot, mapping, textures)。不得先调用再让 generic setGround 丢 map。函数不碰 layer/renderOrder/depth，不强制将桥归 ground。所有 THREE.Texture 预先加载三张 PNG；保持按需渲染。disposeAndRestore 可完整退回原材质/几何。纹理 mipmap 防远距闪纹；没有 runtime shader 时间动画。

预算：增加 0 drawcall、0三角形；3张256² RGBA含 mip 约1MiB GPU纹理；为米制 UV 克隆已命中的路几何，额外 geometry 内存依实际原资产，不冒报手机实测数。材质按原material+纹理复用，保证不把不同桥/ground深度合同合并。

398 actual v143 staging visible v14 runtime GLB道路节点映射测试通过（另有 synthetic测试）：position/index/颜色/depth/layers/order逐项不变且可恢复；实际GLB另外3931非路mesh未污染，worldUV误差≤3.1e-5，开关恢复通过；未跑实际手机GPU。整合到 v15 冻结后由 viewer 作者执行。结构样段 B 的路缘/中央岛不包含在此 A 材质包，不因 A 接入就默认为 B 配准通过。

归属：© OpenStreetMap contributors，源地理映射ODbL-1.0；原创程序纹理：CC BY 4.0，署名 3D_SEU contributors；原创代码：MIT，Copyright (c) 2026 3D_SEU contributors。
