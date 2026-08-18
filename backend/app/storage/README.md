# Storage

`temp/` 是默认临时根目录。MVP 的存储实现在 `services/files.py`：每个任务使用独立目录，下载响应结束后删除，未下载文件由 TTL 清理。
