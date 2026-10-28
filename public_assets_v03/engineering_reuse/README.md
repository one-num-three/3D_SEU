# C3 工科综合科研大楼：旧形体恢复候选

**位置近似待确认，不是精确配准完成。** 单独淡橙集合 `C3_ENGINEERING_APPROXIMATE_LOCATION_PENDING_REVIEW`。新旧源文件均未覆盖，未发布。

- 来源：2026-10-19 clean-ground v2 的 `SW-C3-*`，继承v1的6翼+6屋面，共12个mesh（不是12栋）；烘焙可见倒角后680顶点、672面。
- 身份：旧规划图标号C3／工科综合科研大楼；不是C4工培/工业发展中心，也不是OSM 851764288游泳馆。当前底座没有对应C3的已确认OSM轮廓，所以使用独立稳定ID `SEU_B_LEGACY_PLAN_C3`，不伪造OSM绑定。
- 配准：C2/C4/C5/C6/C7邻近组团质心代理，统一XY相似变换，尺度1.157349、转角4.0993°。RMS 11.22m、最大15.77m、留一最大33.43m；不是测绘角点配准。旧轮廓各翼比例保持，高度不变。
- 旧32m主体估高保留；无可靠观光塔位置，不添加82/85m塔。模型保留两处主要内院；6翼是示意形体而非精细立面。
- 地面实体与当前估宽道路面交叠0㎡、与现有OSM建筑轮廓交叠0㎡，不代表真实通行或测量认证。
- 当前C3不在FULL7/R3D中；恢复候选可追加独立集合，不删除任何当前建筑或道路。

## 入口与复现

`handoff.json`、`LOCAL_REGISTRATION_QA.json`、`C3_BEFORE_AFTER_LOCAL_REVIEW.png`（同范围前后、道路与北向）。

`seu_engineering_reuse_v03.blend` / `.glb` 无图片、字体、Text、外部链接；数据只含实体几何与纯色材质。

```sh
blender -b -t 2 --python rebuild_clean.py -- ./c3_rebuild
```

`geometry_database.json.gz` 为固定校园米制坐标；`source_geometry_database.json.gz` 为旧1.9m/px来源场景坐标，不可直接当UTM坐标。两者拓扑相同、Z值相同；反变换最大float32误差0.0000182m。

`private_audit/` 含源路径和对象属性，仅内部溯源，不随公开包发布。净化模块不含原规划图/私人照片，但移除图片不自动证明旧规划图派生几何可按MIT再授权；公开发布仍由主流程单独审查来源许可。

## Rights boundary
See `SOURCES_AND_RIGHTS.json`. CC BY applies only to our independently authored contributions, not to the original official plan or building design. The transcribed schematic factual outline is explicitly source-identified; university authorization/open licensing has not been established. No map raster, crop, crest, legend, label artwork or decorative map style is included. This is a visibly approximate candidate, not a verified as-built building.
