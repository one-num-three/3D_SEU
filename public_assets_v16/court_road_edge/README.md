# 桃园851764290最小显示裁边（root已审批准纳v16）
原2m默认中心带与明确30个OSM pitch相交538.8128㎡。仅做原polygon减pitch并集，不外扩、不平移路/场/篮架，不补未知道路。剩余545.9343㎡，1连续环带保孔，3连接口保接触；原542.8128m中心线及权限不变。剩余外侧约1m不等于测量宽度或无障碍/规范判定。

replace_object_names 精确仅 SEU_R_OSMWAY_851764290。新GLB1mesh/316tri/0非流形边，旧薄显示板Z .005~.035不变。新leaf仍相同stable_id及layer=road_area，走旧ground order200；先删除/隐藏旧精确对象再加载一份，不双面叠加。微表面A可同ID照常应用，不改变连接。

完整60底座与新面交叠0；未移篮架。原30场来自817128594..817128623，其surface=acrylic有明确OSM标签；道路surface仍未知。前后叠图只用源几何/模型底座，不含版权源照片。

复建：python scripts/build_edge.py → python scripts/plot_and_check.py → blender -b --python scripts/build_model.py。依赖Python3/libgeos_c、matplotlib（仅画图）、Blender4.3。inputs仅地理数据和已生成底座几何，非私图。

© OpenStreetMap contributors，地理及派生数据ODbL-1.0；原创模型贡献：CC BY 4.0，署名 3D_SEU contributors；原创代码：MIT，Copyright (c) 2026 3D_SEU contributors。离线QA不代表手机止闪，最终实际v16+v04近景由主作者渲染核验。
