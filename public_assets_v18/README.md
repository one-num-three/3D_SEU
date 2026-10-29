# 教学区内部道路：局部去同面与柏油显示候选

局部修复增量，原 v17 保留不覆写；发布状态以仓库实际提交为准。

## 范围与证据
仅12条原有内部道路/入口接入段；保持当前原路面并集、中心线、稳定ID、估计宽度及顶/底高程。原图层依OSM中心线buffer生成，接头有重复同高顶面；本候选分配唯一平面归属，不把这些重叠说成现实道路错误。

4条连续内部主路（300162249、630432677、630432678、632703303）按用户对教学区现场的说明，表达为柏油路，不新增独立人行道、盲道、斑马线、路缘或设施。300162249包含向西的连续教学入口接道，632703303包含南端接入，明确不是把全校road类改为柏油。颜色RGB为显示估计，不是测色。其余8条短连接保原PBR，不冒称入口铺装实测。外围两江东路B2有独立照片证据，保持不变。

12个旧对象精确替为12个新对象，原并集1801.269265㎡；重复计面60.340697㎡消除，不等于减少真实铺装面积。实际GLB回读覆盖对称差约0.000258㎡、最大两面交叠0.00000938㎡，为float32量化残差；不是米级现场定位精度。导航数据没有改动。

## 完整源与增量
完整当前主体为4204对象（不是建筑数），4192未涉及对象几何/世界矩阵/PBR不变。道路重复面的正确性修复使整模三角数从3,769,985降至3,769,681；不是LOD减配，没有删除有效路面覆盖或楼体细部。

- assets/SEU_campus_full_quality_v18.blend.zip.001/.002：无损分卷。运行 `python scripts/unpack_full_source.py` 校验并恢复完整Blend。
- assets/SEU_building_patch_v18.glb：网站小增量；data/REPLACEMENT_MANIFEST.json精确替换12对象，禁止叠加旧面。
- `blender -b --python scripts/integrate_checkpoint.py -- PATH_TO_UNPACKED_V17_BLEND`：SHA固定原公开v17后执行整合。

## 文件与检查
- assets/SEU_TEACHING_ROAD_PARTITIONS_v18.blend / .glb：独立12件模块，只按替换清单集成，不能直接追加重叠。
- data/TEACHING_ROAD_GEOMETRY.local.json.gz：完整可复建最终网格/PBR/稳定ID。
- data/ORIGINAL_ROAD_GEOMETRY.local.json.gz、SOURCE_ROADS.local.geojson：原路面及OSM中心线/语义证据。
- data/PARTITION_RECORD.json：确定性归属次序、每件原/新平面及面积差。
- blender -b --python scripts/rebuild_module.py：重建模块（无需参考图片）。
- qa/：实际导出覆盖/网格/导航保留记录。预览为同机位Cycles源工程渲染，不保证手机像素或FPS。

共享坐标不变：EPSG32650原点E671709.6990725585/N3529586.400278158；Blender东/北/上、米。禁止整体抬高路面或为美观挪楼。

© OpenStreetMap contributors：地理事实与派生数据库ODbL1.0 https://opendatacommons.org/licenses/odbl/1-0/ 。©2026 3D_SEU contributors：原创视觉贡献CC BY4.0 https://creativecommons.org/licenses/by/4.0/ ，原创代码MIT。无私有照片像素/来源ID，现场说明只作范围明确的材质参考，不证明路宽/人行通行合规。

材质兼容说明：当前Blender支持的原Principled参数逐项核对保留；旧文件残留的Weight=0及在Subsurface Weight=0时不生效的旧Subsurface IOR插槽在新节点架构中不可用，原数值仍存数据库，详见TARGET_PBR_ID_QA；未抛弃生效的路面纹理或反射参数。
