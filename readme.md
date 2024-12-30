# 双向音频转发示例

本项目演示了如何在 **Mac** 上使用 [**BlackHole**](https://github.com/ExistentialAudio/BlackHole) 虚拟音频设备，将远程客户端的麦克风声音当作 Zoom/Teams 麦克风输入，并将会议输出再传回给客户端播放。实现技术基于 **Python** + **PyAudio** + **Socket**，包含 **自动重连** 等逻辑。

---

## 目录结构

```plaintext
.
├── README.md               # 你现在查看的文件
├── client_in_auto.py       # 客户端：采集麦克风 -> 发送给服务器
├── client_out_auto.py      # 客户端：接收服务器音频 -> 播放
├── server_in_auto.py       # 服务器：接收客户端音频 -> 播放到 BlackHole
├── server_out_auto.py      # 服务器：录制 BlackHole -> 发送给客户端
```
## 环境准备

1. macOS 安装 BlackHole 2ch & 16ch
在服务器（Mac）上，需要同时安装 BlackHole 2ch 和/或 BlackHole 16ch。 可使用 Homebrew：

~~~
brew update
brew install blackhole-2ch
brew install blackhole-16ch
~~~

安装后，在 “系统设置 -> 声音” 或 Audio MIDI Setup 中可看到 BlackHole (2ch) 和 BlackHole (16ch)。

如果你只想使用单一版本，也可只安装 blackhole-2ch 或 blackhole-16ch。示例脚本中会尝试匹配其中一个。

2. Python 环境
Python 3.7+
建议使用虚拟环境（venv / Conda）来管理依赖。
PortAudio & PyAudio
在 macOS 上先安装 PortAudio，再安装 PyAudio：
~~~
brew install portaudio
pip3 install pyaudio
~~~
Windows 或 Linux 一般直接 pip install pyaudio 即可。
3. Windows / 其他平台客户端
在 Windows / Linux 上运行 client_in_auto.py 与 client_out_auto.py 只需安装 Python 3 + PyAudio：
```
pip install pyaudio
```
无需安装 BlackHole；那是服务器端 的 Zoom/Teams 虚拟音频需求。
配置 Zoom / Teams
Zoom/Teams 麦克风 = BlackHole (例如 “BlackHole 16ch”)
Zoom/Teams 扬声器 = BlackHole (例如 “BlackHole 2ch”)
这样会议输入/输出都走 BlackHole，方便 Python 脚本获取和播放。

## 使用步骤
1. 在服务器 (Mac) 上启动服务
打开两个终端，分别执行：

```
python3 server_in_auto.py
```
监听 :50007，等待客户端的麦克风流。
收到后播放到 BlackHole，供 Zoom/Teams 当麦克风。

```
python3 server_out_auto.py
```
监听 :50008，录制本地 BlackHole（Zoom/Teams 输出），发送给客户端。
若发生 overflow，将丢弃一些数据而不抛异常。
脚本运行后，看到类似：

```
[server_in] Listening on port 50007, ...
[server_out] Listening on port 50008, ...
```
表示已就绪，等待客户端连接。

2. 在客户端上运行
修改 client_in_auto.py 和 client_out_auto.py 中的 SERVER_IP 为 Mac 的 IP（如 192.168.31.244）。

在命令行执行：

```
python3 client_in_auto.py
```
将本地麦克风音频发送到服务器 :50007。断线会自动等待 5 秒并重连。
再在另一个命令行执行：

```
python3 client_out_auto.py
```
连接服务器 :50008，获取会议音频并在本地扬声器播放。若断线也会自动重连。

## 功能验证
客户端 对着麦克风说话：

client_in_auto.py -> server_in_auto.py (播放到 BlackHole) -> Zoom/Teams 当作麦克风 → 远程会议可听到。
会议 (Zoom/Teams) 中其他人说话：

Zoom/Teams 扬声器输出 -> BlackHole -> server_out_auto.py -> 客户端 client_out_auto.py 播放 → 客户端能听到会议声音。
## 常见问题
无法连接/超时
1. IP 是否正确； 
2. 客户端和服务器是否同网段；
3. 防火墙端口（50007/50008）是否打开。
4. BlackHole 找不到
检查脚本中 find_device_index_by_substring() 关键字与实际安装名称 (blackhole 2ch / blackhole 16ch) 是否匹配。
是否成功安装了 BlackHole。
5. Overflow
脚本中 exception_on_overflow=False 遇到缓冲区溢出不会抛异常，但数据可能丢失少量音频帧。
若 overflow 频繁出现，可加大 CHUNK 或降低 RATE。
6. 声音太小 / 回声
Zoom/Teams 可调节麦克风增益；
回声可以用耳机或专用回声消除方案（如 WebRTC）。
7. 延迟
纯 TCP + PCM 处理会带来百毫秒级延迟；需更专业的 RTP/WebRTC 才能显著降低。
