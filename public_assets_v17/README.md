# 九曲桥照片比例纠错 · v17

本批已通过源工程冷开与导出核验，发布状态以仓库实际提交为准。不是测绘成果，也不表示 2026 年改造工程已完工。

## 改动
- 保留 OSM 九曲桥中心路线和全部 552 个桥体组件。工作宽度从 4.6 m 调整为 7.5 m：这是依据学校官方航拍的相对比例、经视觉审阅采用的估计，不是实测宽度。
- 保留 551 个非桥面组件的拓扑、原 PBR 材质与 Z；随宽度改变边缘位置。桥面重新分区为浅灰底和六段疏密不一的灰色曲线铺装，不叠加同面涂片，不恢复已取消的红色立体波浪。
- 新增四个平面接岸/种植边界表达；照片内的叶状形态作为平面场地表达，不虚构架高雕塑。位置、颜色和内部尺寸均为照片比例近似。
- 精确替换四条既有道路的显示面，扣除新增接岸铺装，保留导航中心线与车行道路。没有把估计路宽表述为实测或通行合规。
- 桥高、水面及净高没有新实测依据，本批不改变旧显示高程。

本增量替换 556 个当前可见节点，新增 560 个；当前主体为 4204 个网格对象（不是建筑数量）。其余 3644 个对象的几何、世界矩阵、材质保持一致。

## 打开与复建
- `assets/SEU_campus_full_quality_v17.blend.zip.001/.002`：无损分卷；运行 `python scripts/unpack_full_source.py` 校验并恢复到同一 assets 目录得到 `.blend`，可直接打开的当前全校主体工程。保留历史完整细节，不包含独立 v04 地表、程序树和 v16 B2 道路模块。
- `assets/SEU_building_patch_v17.glb`：供网站有序增量替换，不可直接追加造成重叠。
- `assets/SEU_Jiuqu_bridge_photo_proportion_v17.blend` / `.glb`：独立桥及接岸模块。
- `python scripts/validate_release.py`：检查公开文件完整性。
- `blender -b --python scripts/rebuild_module.py`：由随包几何数据库重建独立模块。
- `blender -b --python scripts/integrate_checkpoint.py -- PATH_TO_V16_BLEND`：从公开 v16 源（SHA 见整合 QA）执行精确替换。
- `blender -b --python scripts/validate_checkpoint_blender.py`：先解压全校 Blend，再冷开和 glTF 回读核验。

米制坐标：EPSG:32650，原点 E671709.6990725585 / N3529586.400278158；Blender 东/北/上，glTF 东/上/南。禁止改原点、整体比例或稳定 ID。

## 显示与证据边界
原玻璃栏板透射材质保留，不为性能删减网格。静态 Blender 图不证明手机 WebGL 无闪烁或帧率达标。v16 网站球场黑色问题是地表渲染层灯光配置缺失，正在独立显示修复；本桥源验收不替代实机复测。

`data/SOURCE_EVIDENCE.json` 列官方来源及未测量项；源照片像素不分发。学校照片年代未确认；2026 招标/中标文件不是竣工现状或尺寸证明。当前几何是参考支持的纠错模型，不是竣工数字孪生。

## 署名与分层许可
© OpenStreetMap contributors：地理数据库及其事实修改适用 ODbL 1.0。© 2026 3D_SEU contributors：原创模型/材质贡献 CC BY 4.0，原创代码 MIT。第三方照片、地图艺术表达与建筑设计不因本项目而获得重新授权。详见 `licenses/README.md`。源几何数据库和修改数据随包提供；原 v01–v16 保留不覆写。
