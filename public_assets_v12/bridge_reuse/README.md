# 九曲桥历史细节恢复候选

独立候选，未集成主场景。552网格来自已登记的旧R3D：桥面1、护栏382、边条/花槽105、露出短撑64。没有新增建筑、没有红色波浪。用户历史明确要求取消红波浪，本候选禁止恢复该装饰。

## 地理与高度
米制EPSG:32650，局部原点E671709.6990725585/N3529586.400278158；Blender X东Y北Z上，GLB X东Y上Z南。保持原XYZ不平移/旋转/缩放。路线为OSM way630436309，7段149.6875m；桥宽4.6m为旧照片参考估计，不是实测。当前底图的2m道路宽同样是默认估计。

桥面Z[-.17,.08]、护栏最高1.13，栏高约1.05m。当前水面显示Z=-.003，因此桥底低于水面.167m；Z是旧显示基准，不是桥底净高/水深测量。没有调整全校水位或擅自抬桥。结构支撑水下部分被水面遮住是预期，不能据此判断真实基础。

## 集成
`data/INTEGRATION.json`给精确552新增对象名，`replace_names=[]`。保留`SEU_R_OSMWAY_630436309`的地理线、导航记录及属性，不删除路。新mesh `stable_id=SEU_BRIDGE_OSMWAY_630436309`、`layer=bridge_structure`，应使用正常3D深度pass，不归到ground叠层。路线与水体相交是合法bridge= yes，不是普通道路冲突。桥面高于原道路顶4.5cm；前端如仍显示重复道路，最多隐藏重叠道路的视觉副本，保留原数据。

岸端与北路300030311、南路300176516中心线连接误差0（同OSM节点）。桥面端到道路顶差4.5cm仍是显示差；没有造台阶/岸坡补偿。护栏不穿中心路径，最近距中心线2.185m。端头真实宽度渐变待核。

## 来源/权利/限制
© OpenStreetMap contributors；地理源及其派生数据库ODbL-1.0。原始路线链接：https://www.openstreetmap.org/way/630436309 。自有程序建模视觉表达© 2026 3D_SEU contributors，CC BY4.0；代码MIT。参考照片不随包分发，不给照片/桥梁设计第三方权利重新授权。

旧来源标记PHOTO_AERIAL_2021、PHOTO_SIDE_2020、PHOTO_AERIAL_WHOLE_2020保留为历史证据ID；本次只核旧几何继承与地理配准，未重新确定照片URL/现状，不能把旧照片近似升级为实测。宽度、透明护栏规格、支撑数量尺寸、座凳/花槽外观和绿植均估计。无基础/水下结构、无红波浪。

## 文件与复建
- source_geometry_database.json.gz：旧模块实际求值后的完整世界坐标几何/材料。
- registered_geometry_database.json.gz：最终同一几何数据库，语义内容与source完全一致，未改XYZ。
- ORIGINAL_RAW_FINGERPRINTS.json：原网格局部拓扑指纹和世界变换。
- `blender -b -P scripts/rebuild.py` 从完整数据库重建独立Blend/GLB。
- `blender -b -P scripts/validate.py` 冷开与GLB重导入核验。
- `scripts/render_review.py`生成带原水面/两岸的实际几何预览（上下文只用于图，不在桥GLB内）。材质预览使用Workbench，透明填充显示不等于WebGL真实透射效果。
- qa为已运行检测；最终全校树/其它结构整合排碰尚由主集成阶段执行。

资产无图片、字体、文本块、外链库。552件只有7480三角，仍建议前端按材质/空间合批减drawcall，不改author源。
