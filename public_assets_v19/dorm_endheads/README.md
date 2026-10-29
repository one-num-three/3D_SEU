# 桃园 1–2 宿舍端部细化 / Taoyuan terminal roofs

独立候选补丁，2026-10-29；不是整校替代文件，也不表示网页已更新。

## 本次完成
- 八栋（稳定 ID 630136421–630136428）的 16 个端部坡屋顶及支承墙带；保留中段原坡面、全部深色屋顶板、既有六层窗和 v16 窗梃共面修正。
- 16 个端墙各 5 个上层窄窗，共 80 个。类型有照片支持；具体窗宽、分格、层间高为估计。
- 仅替换 INTEGRATION.json 内 8 个旧屋面，增加 48 个对象。基于 v17 的实际独立合并保存为 4244 网格，其他 4196 网格几何/材质指派/变换未变。
- GEOMETRY_QA.json 披露每栋参数：端部宽约 7.2 m、端檐 z=20.65 m、峰 z=23.05 m。局部 z 是继承的展示标高，不是实测海拔。屋顶板与新增头部有至少 0.5 m 平面间隔。

## 查看与复建
`seu_taoyuan_endheads_candidate.blend/.glb` **仅包含补丁的48个网格**。完整外观请看 AFTER_GROUP / AFTER_END_DETAIL / AFTER_END_FACADE；BEFORE 文件为同镜头对照。END_FACADE 单独显示被核目标楼，避免邻栋遮挡；另外两组保持8栋群。图为 Workbench 审查渲染，不是手机实测。

- Blender 4.3.2 实测。`blender -b --python rebuild_clean.py -- ./rebuilt` 从 geometry_database.json.gz 无第三方 Python 依赖复建小补丁。
- 修改参数：Python 3 + NumPy + Shapely 2，`python build_patch.py`；然后 `python validate_geometry.py`，再执行上面 Blender 复建。footprints.local.geojson 与 baseline_taoyuan_geometry.json.gz 已一并提供。
- 独立维护者合并：`blender -b --python integrate_and_verify.py -- /path/to/current.blend ./review`。脚本验证8旧屋面指纹；源文件只读，新检查点输出 review/campus_with_taoyuan_endheads.blend。可应用于仍保留这些原屋面的 v18 后继基底；必须针对最终基底再次运行。
- `blender -b --python validate_export.py` 冷导入 GLB，核坐标双向最近顶点误差、三角数、稳定 ID、BaseColor/粗糙度/金属度。
- render_compare.py 用已保留的基线数据库重建同镜头对照。导出 PNG 后应剥离文本元数据，不改像素。

## 验证边界
ROOF_AND_WINDOW_QA：无退化/朝下顶面；屋顶投影微小浮点缝隙或重叠上限 0.005 平方米，报告保留实际数，不声称绝对零。新窗玻璃与窗梃前面至少约 0.035 m 分离。EXPORT_QA 为本次真实冷导入。INTEGRATED_QA 为本次实际 v17 合并，非 v18 发布结果。

未调查入口和室内；不添加虚构门、不建立导航。墙端窗数量/尺寸与结构细部仍是合理照片估计，不能称逐栋测绘精度。手机 GPU、闪烁、帧率未测。梅园和橘园既有细部未改；本补丁不能称全校园宿舍全部精修。

## 坐标
米制；EPSG:32650，原点 E=671709.6990725585,N=3529586.400278158；Blender X东 Y北 Z上。GLB 标准 Y-up，X=x,Y=z,Z=-y。不得移动/归零整个补丁、缩放校园，或覆盖完整模型为该小 GLB。

## 来源与许可
公开照片参考：周琦工作室/东南大学建筑设计研究院提供的泳馆项目航拍，2023 年项目文章：
https://www.gooood.cn/natatorium-of-southeast-university-by-zhou-qi-studio-architects-and-engineers-associates-of-southeast-university.htm

俯视及两个斜视可辨同组8栋端部抬高坡顶与端墙上层窄窗；仅作外观证据，不包含原照片或纹理，不重新授权其建筑设计/摄影版权。

OSM 轮廓 © OpenStreetMap contributors，ODbL：https://www.openstreetmap.org/copyright 。代码 MIT；本次原创模型/参数与审查图 CC BY 4.0，署名 3D_SEU contributors。已有基底许可继续适用。预览坐标、米高不是实测保证。
