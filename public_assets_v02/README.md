# 全校建筑样板 v0.2：估高体块＋已做模型合并

这是**全校范围的概念样板**，不是完成全部立面或实测高度。v0.1不覆盖，源模型不破坏。本目录可独立下载、打开和复建。

## 打开模型
- [`assets/SEU_campus_massing_v02.glb`](assets/SEU_campus_massing_v02.glb)：整体GLB，下载后导入glTF查看器；GitHub普通文件页不保证直接预览3D。
- [`assets/SEU_campus_massing_v02.blend`](assets/SEU_campus_massing_v02.blend)：整体Blender工程，建议Blender4.3或兼容版本。
- `previews/CAMPUS_OBLIQUE.png` / `CAMPUS_TOP.png`：斜视与俯视。

![全校样板](previews/CAMPUS_OBLIQUE.png)

**图例**：浅棕体块=估高样板；有窗格/原配色的模型=保留的既有工作细部；红色及其他0.35m低薄片=通道、狭边或施工示意，不代表真实楼高；底图建筑轮廓板不等于新增一栋楼。

## 201个源轮廓逐项交代
权威清单是`BUILDING_STATUS.json`，**源轮廓不等于独立建筑数量**：
- 9个源轮廓保持v0.1教1–8＋体育馆真实细部，共239组件。
- 14个额外源轮廓复用已有1133组件，含图书馆、文科/信息/能环/生医/土木及旧主翼。6个复合或部分精细轮廓不硬塞实心体；8个旧主翼只在实际投影之外补体，不重复整轮廓挤出盖掉细节。
- 166个其余源轮廓生成整轮廓估高体块。
- 6个其余源轮廓只保守作低薄示意（已知穿楼通道、窄连接或construction）。
- 6个桃园西待核源轮廓按此前要求暂缓，仍保留底图，不新建体块：998738587、1056927516、1056927517、1056927518、1056927519、1056927521。不把整个桃园或梅园随意排除。

新增体块模块共194组件：166整轮廓体块＋14局部宽端补体＋14低薄组件（部分来源有多个组件）；不是194栋新楼。组合共2166个mesh，含600基底mesh、239保留细部、1133额外复用、194样板组件。

## 高度、庭院与未匹配项
有可解析OSM height时优先；其次building:levels×假设3.2m层高；否则用解释明确的类型默认值。层数换算和默认值仍标estimated，未分类building=yes采用保守4m，不声称实测。小数值标记高度不是物理净高。

保留源多边形凹口、已有模型围合孔和已映射孔。当前OSM源是简单闭合way、无建筑多面关系内环；**没有记录的真实庭院/通道仍可能未知**，不能由此声称全校真实庭院均已准确恢复。已知穿楼通道不挤成高墙，8主翼补体采用source-minus-reused-mask，宽端块与窄边条分开；不移动道路/原点来消除冲突。

198件定位/形状带待核标记的旧组件未硬塞回，原因见`reused_detail/UNMATCHED_REUSE_REVIEW.json`。它们的旧源文件未删除；不能把这些组件数量当作198栋未建楼。复用轮廓的覆盖缺口/外部附属台阶等见`reused_detail/BUILDING_COVERAGE_REVIEW.json`，不冒称整栋完整。

## 坐标、来源、复现
米制，Blender X格网东/Y格网北/Z上，EPSG:32650固定原点E671709.6990725585、N3529586.400278158；GLB标准Y-up：X=x,Y=z,Z=-y。Z无测绘高程基准。道路及v0.1输入几何不变。

- `base/`：不可变v0.1 OSM快照、WGS84/local基底和源码。
- `detail/`：不可变v0.1已做教楼/体育馆几何数据库与源码。
- `reused_detail/`：本轮清洁复用的最终完整几何数据库、来源覆盖/未匹配清单、复建脚本。
- `massing/`：全部高度/排除配置、源数据、实际mask、生成数据与相对路径脚本。
- 重建模块参考各子目录README。合并：`blender -b -t 2 --python scripts/integrate_v02.py`。
- 文件校验：`python3 scripts/validate_release.py`；组合冷开/回导：`blender -b -t 2 --python scripts/validate_models.py`。
- 自有源码使用MIT；地理数据处理需要系统GEOS/PROJ，离线模型复建需要Blender。仅验证当前主机，不声称跨系统全测。

可见几何直接复用，不减面。GLB省略冗余法线/UV，由viewer重算法线，光照可能不同；保留可编辑Blend。没有照片、卫星像素、纹理文件、字体软件或私人路径/凭据。

## 许可
原创视觉贡献：©2026 3D_SEU contributors，CC BY4.0。OSM及派生地理/几何数据库：©OpenStreetMap contributors，ODbL1.0。代码：MIT。许可证链接/条款见`licenses/README.md`，不能把整个GLB数据库一概改成MIT。每个来源模块的许可及最终输入数据随包提供，不是只给最初OSM而缺失后续新增几何。

本目录由独立`ASSET_MANIFEST.json`覆盖，不改变v0.1的清单。准备检查通过不代表已经推送远程仓库；此文件不声称发布动作已执行。
