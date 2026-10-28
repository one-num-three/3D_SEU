# 校园拟真第一阶段 · v05稳定检查点

**本轮更新：游泳馆1座 + 桃园8条宿舍 + 梅园九舍4条宿舍**，不是全校已精细完成。总网格2783不代表2783栋楼。原v01–v04保留。

## 真实纠错，而非只换颜色
- 游泳馆旧6件没有丢，但只是平顶切角灰盒。本版替换成7组陶红交叉拱、玻璃分格、混凝土边及东侧入口。外廓改为实景支持的矩形，仍在原OSM范围内，中心和朝向不变；116×40m及壳曲率是估计。主屋面11.05m取官方2019设计指标，不宣称实测；接缝最高11.085m。
- 桃园1/2组八条、梅园九舍四条：旧墙体被错误注册成梯形，旧窗实际仅5排。本版在每栋OSM轮廓内重建矩形六层墙窗、坡屋面与可见材料。具体窗距、坡高、颜色和屋面板数量仍为估计；保留院落与道路，不把围合整院填实。
- 梅园九舍没有照抄桃园屋面面板。未见清楚的入口、架空层、阳台不编作已确认。
- 其余2672个原网格的顶点/拓扑/变换逐对象指纹保持一致。低薄投影/残余标记仍不是实际矮楼；原楼高很多仍属估算。

## 打开与网页增量
- `assets/SEU_campus_photorefined_v05.blend`：完整可打开校园检查点（不含可选程序树）。
- `assets/SEU_building_patch_v05.glb`：111个网格的小增量，不是完整校园GLB。载入固定v03原GLB，按`data/REPLACEMENT_MANIFEST.json`精确删除54个旧对象节点，再追加本GLB。必须保留原OSM投影底板及所有不在名单中的节点。不能把旧、新模型一起重叠显示。
- 底图继续用独立`public_assets_v04`；不把建筑v05与展示底图版本混为一谈。
- 真实材料色应保留，不能再用全局灰色覆盖红陶瓦/青绿色屋顶；候选C3、兰园的近似定位提示仍保留。

## 来源与验收
各模块README、参数/geometry_database、INTEGRATION及QA记录证据、估计和精确替换清单。外部实景为学校/设计院供稿，原像素未公开。`data/BUILDING_PROGRESS.json`区分本轮重建/既有保留/未细化，不以网格数量冒充楼数。

本轮最终投影均位于接受的单楼OSM范围内；不等于OSM达到测绘精度。已做冷开、GLB回读、原网格不变、嵌入图像/外链及私密路径扫描；真机帧率由网页测试另报。全校三角面约233万；本轮不是承诺所有手机都流畅。

## 复建
```sh
blender -b --python public_assets_v05/pool_patch/scripts/build_pool.py
blender -b --python public_assets_v05/dorm_patch/rebuild_clean.py
blender -b --python public_assets_v05/meiyuan9_patch/rebuild_clean.py
blender -b --python public_assets_v05/scripts/integrate_checkpoint.py
python3 public_assets_v05/scripts/validate_release.py
```
模块rebuild_clean默认写入各自`rebuilt/`，若替换正式输入需先审查输出再显式复制；integrate只读取冻结模块Blends，不自动采用未审查输出。需要Blender4.3+；参数生成器额外依赖numpy/scipy/shapely，数据库复建不需要这些包。

许可：地理数据ODbL，自创表现CC BY4.0，代码MIT，详见licenses。没有重新授权第三方照片或建筑设计。
