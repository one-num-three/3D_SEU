# 3D_SEU AI 协作框架 v0.1

仓库：https://github.com/one-num-three/3D_SEU

这是九龙湖校园重建项目的轻量 AI 协作框架首发文件：任务认领、独立模块、交接证据与统一验收。**不包含完整校园3D模型、照片、卫星图或完整地理几何。**模型仍需逐资产来源审核，不是此框架发布后自动开放。

本框架代码与文档采用 [MIT License](LICENSE)，Copyright (c) 2026 3D_SEU contributors。第三方地理数据、影像、字体及模型资产不因本LICENSE被重新授权；见 [NOTICE.md](NOTICE.md)。

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

v0.1发布文件已准备；此说明不宣称远程提交已经完成。`init --root .`会在空工作区创建各任务module目录，不需要先有模型文件；真实任务仍需获得授权输入。
