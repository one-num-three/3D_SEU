# 文科A楼 — 旧资产复用＋实拍约束候选

独立候选，未集成、未发布；不是C17。针对OSM300030306，依据R7 C15_lower_s五件历史资产与学校2012明确标“A楼”的实拍，恢复主要外形，不能称全部已完成实景测绘。

## 本轮不是只搬24m平顶
原body/footing拓扑复用；旧框和玻璃组件按可用区域保留，移除第6行，改为5行。旧24m估高和平顶已明确弃用：主体18.4m、坡脊19.7m、端塔顶22.7m均是**根据可见五层的米制估计，不是实测**。新增浅坡深灰屋面、西南端塔/挑檐、相邻南侧竖玻璃带和分格。照片可直接读到“A楼”字样；牌字不复制贴图，未知入口/内部不编。

端塔位于西南、玻璃位于南侧是结合三条楼透视退远及西连段的推断；镜头无GPS/朝向记录，保留orientation_status。参考为2012历史图；2024改造设计公示不能证明2026外观未变。未见北/东面保持简化，不说逐面确认。

## 坐标与精确替换
只remove `SEU_B_OSMWAY_300030306.001`，保留无后缀原轮廓；append `data/REPLACEMENT_MANIFEST.json`列出的12 mesh。其他C15两条已恢复的B/C、lower_n、lower_e、连接段均不动。

本地米制EPSG32650偏移原点(671709.6990725585,3529586.400278158)。X东/Y北/Z上；GLB X东/Y上/Z南。整体XY采用单一正交局部轴线映射，窗不做梯形扭曲或裁平；安全包络55.6025×14.8694m在原OSM面内缩至少0.30m。面积/路宽仍是已接受工作底图，不是测绘精度。

## 文件与复建
`assets/SEU_c15_a_reuse_candidate.blend` / `.glb` 是最终12件候选。`data/source_geometry_database.json.gz`保存原五件完整评估后几何/材质；`original_raw_mesh_fingerprints.json.gz`保存原raw指纹；`registered_geometry_database.json.gz`为最终几何。`SOURCE_TO_REFINED_CHANGES.json`列逐源组件保留/删除原因、窗组件索引与高度改动，不能把最终网格谎称与旧源逐顶点完全相同。

`python scripts/refine_from_source.py`从完整旧几何与参数重新产生最终数据库；`blender -b --python scripts/rebuild.py`导出Blend/GLB；`blender -b --python scripts/validate.py`冷开/重导入检查；投影QA见qa/PROJECTION_QA.json。预览为实际候选渲染，非原景照片/网页截图。

## 权利/隐私
代码MIT，自制视觉贡献CC BY4，地理数据库ODbL，见licenses。© OpenStreetMap contributors；©2026 3D_SEU contributors。无原图像素、无字体软件/贴图/私密路径。照片只列公开来源，不转发。候选仍需主场景与树林避让复核，不自行推远端。
