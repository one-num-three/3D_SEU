# 协作与交接

## 单一负责人
状态为queued→claimed→submitted→validated→merged。当前CLI执行到validated；真正merged由维护者记录实际合并提交/清单，不由worker自报。任务输入使用`project_contract.json`指定的公开版本文件/SHA；旧框架任务只供历史理解。

在同一受信共享工作区：`python tools/coop.py init --db coordination.sqlite --tasks tasks.json --root .`，随后claim自己的task。SQLite BEGIN IMMEDIATE与条件状态转换阻止同一数据库双认领；actor是声明名字，不是身份认证。不要复制数据库到各机器后称其为全局锁，不设自动超时抢锁。已有数据库不能init重置；更换任务轮次须先由维护者关闭/归档旧认领，再建立新的单一协调台账，不能另开DB绕过未完成的owner。

跨机器：用单一维护者的认领PR/台账串行核准owner，分支`task/<ID>/<actor>`。仓库已存在于 https://github.com/one-num-three/3D_SEU ，但本工具没有远程自动认领/PR发布/跨机器锁服务。实际协作权限由维护者控制。

## 模块与证据
候选只能写task.write_prefix。输入是固定公开检查点、模块manifest/源码事实与公开参考；私人原图不是每个贡献者必须获得的依赖。若某细节确实需要私有证据，先记录缺口或以公开证据重新核验，不发布内部关联信息。

提交evidence包含baseline SHA、artifacts路径/hash、sources权利和适用范围、assumptions、QA报告和必要前后图。`examples/evidence.template.json`的NOT_RUN需要真实检查完成后再改；空模板不能提交。CLI仅验证交接格式/哈希/路径，真正几何和来源必须独立审查。

几何改动要核世界投影、院洞/通道/道路冲突、保留对象/材质、精确替换名单、冷开和GLB回读、树/道具避让。入口/台阶检查不等于导航portal已经实现；手机性能必须区分真机实测、模拟环境和未运行。

## 合并与发布
唯一维护者把通过的模块合到新副本；两个模块若改同一对象，暂停并指定owner重基线，不做最后写入覆盖。先核所有旧补丁继续加载，再做运行时合批，不能直接改已batch后的源可见性。失败回滚，不覆写冻结资产。

新发布须保留分层许可、源事实/生成参数与完整manifest，扫描文本、PNG metadata、压缩Blend、gzip/ZIP；排除__pycache__/pyc和私有照片关联ID。部署成功以具体commit及远端hash/Pages结果为证，不以本地文件生成代替。`project_contract.release_git_commit`由发布者填真实基线提交；新贡献以其实际检出的公开文件SHA为准。
