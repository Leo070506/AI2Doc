# AI2Doc Backend

该目录包含 Milestone 1 的 FastAPI 服务。应用入口为 `app.main:app`。

职责：

- 暴露版本化 HTTP API
- 校验并编排文档生成任务
- 通过受控适配器调用服务器端 Pandoc
- 管理模板目录与临时文件生命周期
- 提供健康检查、错误分类和必要指标

本地启动与测试见 [`../docs/mvp-development.md`](../docs/mvp-development.md)，公开接口见 [`../docs/api-design.md`](../docs/api-design.md)。
