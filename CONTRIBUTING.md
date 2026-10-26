# 协作规则

## 状态与唯一负责人
queued → claimed → submitted → validated → merged。当前实现自动执行至validated；merged必须维护者实际合并并记录Git提交/发布清单后另行记账，不由worker自己说完成。被驳回回到claimed。blocked和撤销/换人通过维护者操作台账，不能删除锁抢任务；当前CLI不实现超时抢占。
每个task只有一个owner，多worker可以读同一基底，不能并写同一个blend。教学worker与体育馆worker并行；道路只改标签。QA是独立审查角色，不能自审；维护者是唯一整图写入人。

## 输入/输出契约
任务输入为固定R3D SHA和只读坐标/ID表；有私有证据需求的worker须在授权环境获取，公开候选不携带凭据。输出是独立collection/module、相对路径manifest、sources/assumptions/explicit_hidden_objects、QA与前后图。所有文件须落在task的write_prefix。
提交CLI校验baseline SHA、文件SHA、路径边界、证据字段与声明的QA状态；这些是交接检查。真正几何QA需另跑Blender检查：mesh实际世界坐标、投影差、道路/院落冲突、隐藏替换、附属光伏、冷启动。QA reviewer必须看报告和图，再确认review，不可只看CLI退出码。

## 合并/冲突
维护者按依赖拓扑合并模块到新副本；若同一对象被两模块改动，暂停该模块，指定单一owner重基线，不做最后写入覆盖。检查原对象指纹，允许隐藏名单必须显式。通过冷开/紧凑版等价/哈希后保存新版本，失败回滚不覆原件。

## 最小接口的信任边界
SQLite BEGIN IMMEDIATE事务和条件状态转换在同一个本地数据库防止双认领；actor是声明身份，不是认证系统，能改数据库文件的人仍有管理员能力。不得当作敌对环境安全隔离。正式Git PR必须启用身份验证与维护者review；本次未配置任何远程仓库。
