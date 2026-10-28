# 校园模型 v0.15：完整体育细部恢复＋钟山书院庭院体量纠错

本版本不是全校实测模型。保留旧版本，不改变校园原点、道路或未列入替换的建筑。共 4110 个作者 mesh，非 4110 栋建筑；3,544,151 三角面。精确替换 305 个旧对象、追加 439 个对象，3671 个旧对象几何与材质保持。

## 打开
- Blender 4.3.2：直接打开 `assets/SEU_campus_full_quality_v15.blend`，包含当前全部建筑/桥/球场。独立地表 v04、603 程序树与可选自行车仍沿用仓库前版，未重复打包；此源不是所有展示层合成场景。
- GLB 增量：解压 `assets/SEU_building_patch_v15_GLB.zip`。这是补丁，不是全校园独立 GLB。用 `data/REPLACEMENT_MANIFEST.json` 对当前 v14 可见对象进行事务替换；旧体育对象来自 v12，不能只搜索原始 v03 名单。
- 归档/member SHA 与字节数见 `data/PATCH_ARCHIVE.json`。ZIP 与 Blend 重压只改变压缩字节，未减面。

## 体育：恢复的是完整作者细部，不是新增测量
404 个原细部 mesh / 1,048,160 三角面；原417中仅13个与基底重复的地板未重复加载。恢复细网、围网丝、环、场线厚度、网带、原 flat normals 和标准 PBR；照片支持的蓝色场面保留。最新核查确认桃园原始OSM共有30个独立pitch（817128594–817128623），并与实景6×5场线布局吻合；本版只恢复历史中间12场，外围18场仍待紧接的独立修补批，不宣称区域铺满。

三种自制程序 Noise→Bump 在完整 Blender 源中原样保留，标准 glTF 尚不能复现；详见 `sports_full/PBR_COMPATIBILITY.md`。这是格式限制，不是默认性能降质。九曲桥全部原几何和原透射参数保留，不恢复已取消的红波浪。

## 钟山书院：明确近似的院落分体纠错
以校方2025/2026施工照片纠正原 9095.25 平方米实心盒填院问题，新增35 mesh。OSM只提供组团外框，**没有独立逐栋 footprint 或控制点精确配准**。内部位置、米制高度、屋坡/廊柱尺寸均估计；不是竣工现状照片精模。外框内楼体投影2034.99平方米、上部投影2348.42平方米；其余并非全部可通行庭院。详见模块README与中文对比图。

## 坐标、复建和校验
EPSG:32650；原点 E671709.6990725585 / N3529586.400278158。Blender east/north/up 米，glTF east/up/south 米，比例1。
完整源可独立打开。增量复建：先分别运行 `blender -b --python sports_full/scripts/build_full_quality.py` 与 `zhongshan_courtyard/scripts/build_candidate.py`，再 `blender -b --python scripts/integrate_checkpoint.py -- <公开v14完整Blend路径>`。模块输出由公开数据生成，不需要私有原图。公开v14前置SHA见材质QA；地理完整前史仍可从仓库相应源目录获取。生成工作副本不要覆盖冻结发布目录。
`python scripts/validate_release.py` 检查文件清单；`blender -b --python scripts/validate_checkpoint_blender.py` 冷开并复验补丁三角形。437对象1毫米网格哈希严格相等，另外2场线以全部三角形一一匹配验证，最大数值误差0.0611毫米。

© OpenStreetMap contributors — ODbL地理事实；原创视觉贡献 ©2026 3D_SEU contributors — CC BY4.0；代码MIT。许可不替第三方照片/建筑设计授权，参考图像不分发。显示渲染为本地模型视图，非手机GPU/FPS实测。

## 发布前接地纠错（不是减配）
实际完整源＋v04合场逐脚射线及整底面XY检查发现：旧12场的24个篮架底脚比真实显示场地高约0.464m，没有承托。故仅这12场各5组件共60对象统一竖向平移 −0.459m，脚底Z=.001，对现有场地Z=−.004保留5mm接合容差；不移动XY、不缩放、不改任何局部顶点/拓扑/法线/材质、不增加重复厚板。篮圈相对脚底高度保持原值。此为对当前平地显示基底的接地校正，**不是实测地理高程**，不能说这60对象世界Z原样恢复。精确名称/矩阵差与前后真实raycast见 `qa/BASKETBALL_GROUND_ALIGNMENT.json`、`BASKETBALL_SUPPORT_BEFORE/AFTER.json`。独立网球全部不动，原桥不动。
