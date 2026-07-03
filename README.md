# VideoAudit-Pipeline 

基于 Python + Tkinter 前端 + FFmpeg 内核的视频自动化合规审计软件。

## 
* *利用 Tkinter 组件实现的简易进度条。
* *内嵌 `ffprobe.exe` 支持零环境运行。
* *审核结果多路分发**：本地自动生成 `report/` 包含 `CSV` 与 `JSON` 记录，同时 TCP 传输结果给云服务器。

## 
* *特别注意：内核封装原理
本项目在开发时源码与二进制内核解耦（Repository 内不包含 `ffprobe.exe` 实体）。只通过编译引擎将内核物理封装人`.exe` 中。
封装时请使用   pyinstaller -F -w --add-binary "C:\你的本地路径\ffprobe.exe;." .\你的文件名字.py
