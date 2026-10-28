# 5分钟接手：实际公开项目，而非空框架

1. 读`project_contract.json`，下载/检出它的`baseline_path`与`baseline_manifest_path`；跑`python tools/validate_contract.py --root .`。不可跳回首轮私有R3D SHA。
2. 完整Blender检查点是编辑输入；固定v03 GLB与`preview/patches.json`的精确替换链继续作为不可变来源。网页默认使用`public_runtime_v14`中与该链等价的无损运行快照，失败不自动下载旧链，需明确选择旧加载方式；这只是下载优化，不提升模型精度或保证内存/FPS。v04地表、程序树和可选自行车仍独立加载。不要只打开一个小补丁就以为整校资产丢失。
3. 阅读当前版本README、数据/来源/假设与QA。模型mesh数不是楼数；201源轮廓也含附属/组合体，不能当201座独立建筑。
4. `tasks.json`是可认领下一步，不是正在运行的worker列表。维护者初始化单一协调DB，worker只领一份明确模块。每项只写自己的prefix，冻结基底只读。
5. 真正做几何之前，核旧细部是否已经保留、名称/使用单位是否混标、是否把上层投影当实墙。产出独立小模块＋来源＋参数＋具体替换清单＋前后图，再独立review/唯一合并。

## 当前边界
- 公开模型已包含基底、旧细部恢复及逐版外观修正，不再是“只有框架无资产”。但仍不是全部实测/精修校园。
- 田家炳北条4排窗属于可见类型参考，不等于全楼4层；南旧高度/窗排仍估。金智的隔离旧核心诊断未进入v14，不要从未发布候选猜主图现状。
- 还有估高体块、近似C3/兰园/亭位置及两处低标记等。正式名称与功能、层数与米高、复用与实景验证分开记账。
- 泳馆门是外观门；体育馆上层平台、桥与台阶需要独立导航层/portal。候选路网不是已实现小人寻路，紧急出口不是普通入口。
- 网页 v0.14.2 质量优先：默认原桥透射、全部 603 棵最高已有细节树、原生像素比（仅真 GPU 尺寸限制会提示降档）；省资源桥栏/画面只由用户手动启用。无损快照、几何不变合批及分层地表保留。体育完整围网源恢复仍待后续批次，不能称全源细节已恢复。解析测试不代替真实手机 FPS，高质量默认可能更耗资源。

## 最小操作
```sh
python tools/test_coop.py
python tools/test_contract.py
python tools/validate_contract.py --root .
python tools/coop.py init --db coordination.sqlite --tasks tasks.json --root .
python tools/coop.py claim --db coordination.sqlite --task NAME-EVIDENCE --actor your-agent
```
用自己的真实产物填写evidence，然后submit；独立reviewer核看报告/图后review。不要提交这里的例子作为校园完成证据。

需要跨机器协作时由维护者认领PR串行授权；本仓库不提供全局锁或自动发布机器人。原始参考照片不必公开，公开事实/源轮廓和生成参数必须足以解释本次贡献。
