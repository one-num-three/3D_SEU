# 游泳馆 v05 外观修复

修复对象 `SEU_B_OSMWAY_851764288`。旧v03的6个网格一直在，但形态为普通切角平顶盒，并未表现真实游泳馆；不是底图把它遮掉。

本版按学校设计院及其提供的2023竣工实景，独立程序化制作7组交叉拱、陶红屋面、清水混凝土边缘、落地玻璃分格、东侧入口。删除精确6个旧占位件，保留原OSM薄投影层。未复制原照片像素、图纸线稿、CAD或纹理。

## 地理与尺寸
原OSM边界、模型中心及朝向不改。纠正旧切角占位轮廓为照片支持的长方形实体，116×40m仅为结合现注册范围和设计院约120×40m施工场地描述的估计外廓，不是测量尺寸；新几何在原OSM轮廓外溢0。主屋面最高11.05m采用学校2019设计指标，非竣工实测；接缝局部+0.035m，实际最高11.085m。壳曲率、厚度、玻璃分格为近似。

## 来源及权利
- 设计院官方说明：https://adri.seu.edu.cn/2023/1225/c56277a511272/page.htm
- 周琦工作室提供的竣工实景与介绍：https://www.gooood.cn/natatorium-of-southeast-university-by-zhou-qi-studio-architects-and-engineers-associates-of-southeast-university.htm
- 设计高度：https://news.seu.edu.cn/2019/0430/c5487a271243/page.htm
- © OpenStreetMap contributors；地理数据库内容ODbL1.0；本项目原创几何表现/材质CC BY4.0，3D_SEU contributors；代码MIT。并不重新授权第三方建筑设计或参考照片。参考图片仅内部观察，未公开分发。

`data/pool_parameters.json`为全部建模参数与限制；`scripts/build_pool.py`使用Blender独立复建；`data/geometry_database.json.gz`保存实际最终几何和材质。此模块不代表整栋内部或校园全部已细化。
