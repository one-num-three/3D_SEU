# 桃园3–8：24栋历史梯形配准纠正候选

2026-10-29，基于公开v20；独立工程候选，未发布。本包只有真实几何纠正，**不含艺术阳台、入口、色带，不批量套用四栋艺术小样**。

## 范围与依据
东北32栋桃园中，1–2八栋已经矩形，不修改；3–8其余24栋旧复用注册呈梯形：主体矩形填充率82.4%–84.9%，对应接受OSM轮廓99.58%–99.88%。逐栋先检查源面矩形比例>99%，再在源近矩形内缩0.60m；24栋全部通过，无本轮形状例外。南部错名630141871排除。梅园/橘园保留。不是强行将任意真实多边形抹成矩形。

照片类型参考：设计院2023泳馆项目航拍（不随包分发）：https://www.gooood.cn/natatorium-of-southeast-university-by-zhou-qi-studio-architects-and-engineers-associates-of-southeast-university.htm 。不是24栋逐楼实测；具体高程、旧窗排/数量继承模型。

## 修正方法与边界
先解原梯形到目标框平面变换；原扭曲倒角在反变后仍遮窗，因此主体和檐口按原对象Z界重建细倒角；旧窗数量110/栋、窗Z保留，侧向重新贴回校正立面。**原拓扑/每顶点XY不保留，不能标零改动。**主体质心回正最大约0.641m，属于原OSM范围内配准纠正，未更改OSM边界/楼间次序/stable ID/坐标原点。

真实纠正96对象（每栋窗框、玻璃、檐口、主体各1），不是新增96栋。原裸OSM投影对象不替换。保原屋顶薄檐口类型和各Z上下界，不猜坡屋顶或入口。

## 执行过的QA
- CORRECTION_QA：24栋全部细部投影OSM外0㎡；各对象Z上下界差0；主体矩形率最小99.99546%。
- MESH_FACE_QA：96对象全部三角无退化。
- EXPORT_QA：GLB冷回读96对象、双向最近顶点世界坐标差0、三角数和BaseColor核对通过。
- INTEGRATED_QA：已实际把候选几何放回v20只读源的独立新副本：总4276对象不变，96几何替换，4180对象世界几何指纹相同。**正式合并脚本复用源材料datablocks**，不以小补丁统一粗糙度代替原材质。
- `corrected/dorm_sample.glb`为小补丁审查导出，PBR粗糙度统一0.65，用于审几何；若整校导出需要严格材质保留，先运行integrate_current.py，再从完整新检查点导出。
- 图为桌面正射/Workbench几何审查，无手机GPU/帧率验收。旧110窗/五排继承，不是逐楼真实窗数认证，相关改进应另立有照片依据任务。

## 复建/合并
1. `python build_rectification.py`：Python3 + NumPy + Shapely2；包内source_dorms.json和footprints.local.geojson，无私有原图依赖。
2. `blender -b --python corrected/rebuild.py -- ./rebuilt`：从数据库重建独立Blend/GLB；Blender4.3.2实测。
3. `blender -b --python integrate_current.py -- /path/current.blend ./campus_rectified.blend`：原源不覆盖；先核96旧对象指纹，更新几何但复用原材质。后继版本只要96源几何未变也可执行；若指纹不匹配必须停核，不强套。
4. `blender -b --python check.py`：冷导入检查独立GLB。
5. 独立维护者review后才能整合发布；不要并加before/corrected两版或用96对象文件覆盖整校。

坐标：EPSG32650，原点E671709.6990725585/N3529586.400278158，米。Blender X东Y北Z上；GLB X=x/Y=z/Z=-y，Z是估计展示标高。

许可：代码MIT；自制可授权视觉贡献CC BY4.0，3D_SEU contributors；OSM及派生地理数据ODbL，© OpenStreetMap contributors https://www.openstreetmap.org/copyright 。第三方设计/摄影权利不重新授权。
