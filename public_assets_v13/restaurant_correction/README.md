# 特色餐厅 OSM171400094：误薄片纠正候选

**Footprint-based correction, NOT photo-refined.** 独立候选，未更改冻结主模型。不是实景立面重建，不含推测窗排、招牌、入口装饰或室内。

## 为什么修
原OSM way171400094记录name=特色餐厅、amenity=restaurant、building:levels=2。前版因局部穿楼通道占投影7.56%，把975.593㎡整楼压成0.35m薄片。这里仅纠正这一楼的逻辑问题，300020025零售及300020029厕所不改；96已有细部的残余薄片不改。

## 几何及估计
源投影有6个非重复节点、0孔洞，保持原边界与坐标。下层减去原road_area通道得到2块落地体，上层完整保留原投影。原3m道路宽也是按cycleway分类估计，不是实测。本候选不删除道路、不堵通道，不将穿楼路径挖成贯穿屋面的假庭院。

两层来自OSM；每层3.2m与总高6.4m属于解释性估计。建筑底Z.12、顶6.52；通道上方下表面3.32，对原路面顶.035净高3.285m，**该净高未实测**。平屋面形式/颜色均中性占位，不称照片确认。当前展示材质为浅中性墙与深中性屋面，正式名称/现状外观仍待核。

## 集成（只替1件）
精确移除旧 `SEU_B_OSMWAY_171400094.001`，加INTEGRATION.json列4件。保留原outline `SEU_B_OSMWAY_171400094`、原道路 `SEU_R_OSMWAY_633558660`、所有其它对象。稳定ID不变，角色building_massing_correction，正常3D pass。预览地面只是上下文，不在资产中。

## 可复建与QA
- SOURCE_FACTS.local.geojson：最终真正使用的建筑/路面事实，含原点/CRS。
- ORIGINAL_OSM_TAGS.json：原building:levels=2等记录与版本/时间，不含OSM编辑者个人信息。
- replaced_original_geometry.json.gz：被替换旧薄片完整几何/属性与原网格指纹。
- registered_geometry_database.json.gz：4个最终网格/纯色材质完整数据。
- PARAMETERS.json：层高/净空假设；scripts/build_data.py从事实生成最终几何；scripts/rebuild.py用Blender生成资产；scripts/validate.py冷开/GLB重导入核验。
- FOOTPRINT_PASSAGE_QA：下层与道路实际交叠0㎡、留空73.762㎡，理论全投影与原边界一致（数值误差约1e-12㎡）。冷开float坐标误差另列，不混淆为测绘精度。
- TREE_CLEARANCE_QA：未改603个实例，树冠到投影最小49.443m，7m门槛通过。

## 来源及权利
© OpenStreetMap contributors，https://www.openstreetmap.org/way/171400094 ，https://www.openstreetmap.org/way/633558660 。地理及其派生数据库ODbL-1.0；本项目自制程序几何表达© 2026 3D_SEU contributors，CC BY4.0；代码MIT。完整输入/估计参数/生成方法均附带；不为第三方建筑设计重新授权。

校方2025梅园食堂页说明双层和二楼北侧民族餐厅： https://zwc.seu.edu.cn/2025/0630/c61646a534624/pagem.htm 。2014校方称梅园苏果超市二楼餐厅： https://zwc.seu.edu.cn/2014/0314/c60881a39592/pagem.htm 。这些仅作周边功能佐证，**不证明本文OSM轮廓与某照片楼翼唯一对应**。没有照片像素/字体/私有路径/凭据入包。
