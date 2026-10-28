# 3D_SEU 校园3D资产与AI协作框架

仓库：https://github.com/one-num-three/3D_SEU

这是九龙湖校园重建项目：轻量 AI 协作框架用于任务认领、独立模块、交接证据与统一验收；`public_assets/`、`public_assets_v02/` 与 `public_assets_v03/` 分版保留已审核的校园基底、工作模型、体块样板和本轮修复。**这不是完整校园最终模型；不附私人照片或卫星截图。**框架与资产分别记录许可和清单，未收录资产不因此自动开放。

本框架代码与文档采用 [MIT License](LICENSE)，Copyright (c) 2026 3D_SEU contributors。第三方地理数据、影像、字体及模型资产不因本LICENSE被重新授权；见 [NOTICE.md](NOTICE.md)。

## 最新预览：v0.4.0 轻快底图与显示修复

[在线查看校园](https://one-num-three.github.io/3D_SEU/) · [v0.4 地表说明](public_assets_v04/README.md)

网页 v0.4.0（2026-10-28）在原建筑模型 v0.3 上叠加同坐标的地表层：106 项 OSM 地表要素及一层底板，区分绿地、水面、运动场和施工区；采用浅暖建筑、柔绿地面与湖蓝水面。道路与地面的深度显示修复属于网页显示层，不改建筑高度、轮廓或既有道路几何。C3／兰园仍是近似位置候选，不代表实测或完整校园。

v0.1、v0.2、v0.3 原资产逐字节保留。新增地表独立使用 `public_assets_v04/ASSET_MANIFEST.json`，网页使用 `preview/FILE_MANIFEST.json`；代码 MIT、自有视觉贡献 CC BY 4.0、OSM 派生地理数据 ODbL 1.0，具体来源和边界见各版说明。无私人照片或卫星截图。

## v0.3 生医南向修正与旧楼恢复

[工程说明](public_assets_v03/README.md) · [全景](public_assets_v03/previews/CAMPUS_OBLIQUE.png) · [完整Blender](public_assets_v03/assets/SEU_campus_restored_v03.blend) · [完整GLB ZIP](public_assets_v03/assets/SEU_campus_restored_v03_GLB.zip)（解压后打开GLB）

生医高楼已改南侧；恢复旧宿舍、学院和游泳馆细部。工科C3和兰园独立标为近似候选，行政及部分翼楼仍待核，不等同全校完成。2726是网格组件数，不是楼数。保留v0.1/v0.2回退。

代码MIT、自有视觉贡献CC BY4.0、OSM派生地理数据库ODbL1.0；C3事实来源及第三方权利边界另列，不将原规划图重新授权。无原始私人照片、卫星截图或第三方纹理。

本版ASSET_MANIFEST独立覆盖174文件（其中173哈希条目＋清单本身）；DEPENDENCIES记录三项固定上版输入。完整模型可独立打开；源复建需整个仓库保留相邻public_assets_v02。

![v0.3全览](public_assets_v03/previews/CAMPUS_OBLIQUE.png)

## 全校体块样板 v0.2

[查看v0.2资产与逐源轮廓状态](public_assets_v02/README.md)：已保留的教学/体育馆及其他已有细部，加其余建筑估高体块；高度/未映射庭院尚未实测。v0.1仍保留。

![v0.2全览](public_assets_v02/previews/CAMPUS_OBLIQUE.png)

[整体GLB](public_assets_v02/assets/SEU_campus_massing_v02.glb) · [Blender源文件](public_assets_v02/assets/SEU_campus_massing_v02.blend) · [201源轮廓状态清单](public_assets_v02/BUILDING_STATUS.json)

数据ODbL、原创视觉CC BY4.0、代码MIT；v0.2由public_assets_v02/ASSET_MANIFEST.json独立校验，不以框架或v0.1清单冒充全仓库清单。

## 已提供的真实3D资产 v0.1

[打开资产目录](public_assets/README.md)：全校OSM建筑/道路基底＋已做教1–8和体育馆。包含可编辑Blend、GLB、源数据库、重建脚本和许可，非完整校园最终模型。

![基底＋已做部分](public_assets/previews/COMPLETED_TEACHING_GYM.png)

- [下载组合GLB](public_assets/assets/SEU_base_teaching_gym_v01.glb)
- [下载组合Blender模型](public_assets/assets/SEU_base_teaching_gym_v01.blend)
- [来源、坐标、许可与重建](public_assets/README.md)

框架代码MIT；原创模型视觉贡献CC BY4.0（3D_SEU contributors）；OSM派生地理数据ODbL。框架根FILE_MANIFEST只描述框架文件，本批资产由public_assets/ASSET_MANIFEST.json独立覆盖。

## 5分钟接手
1. 读 `project_contract.json` 和 `AGENTS.md`。
2. 读 `tasks.json`，选角色；任务尚未启动，角色不是正在运行的AI。
3. 管理员在**同一协调工作区**初始化：`python3 tools/coop.py init --db coordination.sqlite --tasks tasks.json`。
4. worker认领：`python3 tools/coop.py claim --db coordination.sqlite --task TEACH-DETAIL --actor agent-teaching`。SQLite事务提供同一数据库上的唯一认领；单纯提交JSON不提供原子性。
5. 只写自己的module目录，产出证据JSON，再调用submit。独立QA调用review，维护者统一合并。命令帮助见 `python3 tools/coop.py --help`。
6. 自检：`python3 tools/test_coop.py`。

## 多机器 / Git
不能把SQLite数据库复制到各clone再称全局锁。跨机器使用**单一维护者认领台账**：worker开认领PR，由维护者串行核准唯一任务owner后才开工；实际分支 `task/<ID>/<actor>`，模块一人写，共享基底只读，几何修改PR和证据分开审。当前包没有远程协调服务/GitHub自动化，也未验证网络文件系统锁语义。SQLite仅用于本机共享工作区演示和协作。

`docs/RELEASE_READINESS.md`列框架与模型的发布边界；`CONTRIBUTING.md`规定交接。不要把“工具测试通过”解读为全模型许可或几何验收通过。

## 提交与审查例子
```sh
python3 tools/coop.py submit --db coordination.sqlite --task TEACH-DETAIL --actor agent-teaching --root . --evidence modules/teaching_detail/evidence.json
python3 tools/coop.py review --db coordination.sqlite --task TEACH-DETAIL --actor independent-reviewer --root . --decision accept
python3 tools/coop.py status --db coordination.sqlite
```
`examples/evidence.template.json`必须填真实SHA和报告文件；空模板故意不能提交。当前CLI不自动运行几何建模、不替你上传PR，也不管理第三方登录。

框架v0.1已发布；本批3D资产的范围与复核结果见 `public_assets/README.md`。`init --root .`会在空工作区创建各任务module目录，不需要先有模型文件；真实任务仍需获得授权输入。
