# server_in_auto.py
import socket
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

HOST = "0.0.0.0"
PORT_IN = 50007  # 接收客户端(发送麦克风)的端口

def find_device_index_by_substring(p, name_substring):
    """
    在所有可用音频设备中，匹配名称包含 name_substring 的“输出”设备，
    返回其 device_index。如果找不到则返回 None。
    """
    count = p.get_device_count()
    for i in range(count):
        info = p.get_device_info_by_index(i)
        if info.get('maxOutputChannels', 0) > 0:  # 输出设备
            dev_name = info.get('name').lower()
            if name_substring.lower() in dev_name:
                return i
    return None

def main():
    # 1) 创建监听 Socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT_IN))
    server_socket.listen(5)
    print(f"[server_in] Listening on port {PORT_IN}, waiting for client...")

    # 2) 初始化 PyAudio
    p = pyaudio.PyAudio()
    # 假设想输出到 "BlackHole 16ch"；若找不到可换 "blackhole 2ch" 或默认(None)
    output_index = find_device_index_by_substring(p, "blackhole 16ch")
    if output_index is None:
        output_index = find_device_index_by_substring(p, "blackhole 2ch")
    print(f"[server_in] Using output device index={output_index}")

    while True:
        print("[server_in] Accepting new client...")
        conn, addr = server_socket.accept()
        print(f"[server_in] Client connected from: {addr}")

        # 打开播放流
        stream_out = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK,
            output_device_index=output_index
        )

        try:
            while True:
                data = conn.recv(CHUNK)
                if not data:
                    print("[server_in] Client disconnected.")
                    break
                stream_out.write(data)
        except Exception as e:
            print("[server_in] Exception:", e)
        finally:
            stream_out.stop_stream()
            stream_out.close()
            conn.close()
            print("[server_in] Connection closed, wait for next client.")

    # 理论上不会到这里；若要优雅退出可在外层加异常处理
    p.terminate()
    server_socket.close()

if __name__ == "__main__":
    main()
