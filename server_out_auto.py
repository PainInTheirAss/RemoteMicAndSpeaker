# server_out_auto.py
import socket
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

HOST = "0.0.0.0"
PORT_OUT = 50008  # 发送音频给客户端的端口

def find_device_index_by_substring(p, name_substring):
    """
    在所有可用音频设备中，匹配名称包含 name_substring 的“输入”设备，
    返回其 device_index。如果找不到则返回 None。
    """
    count = p.get_device_count()
    for i in range(count):
        info = p.get_device_info_by_index(i)
        if info.get('maxInputChannels', 0) > 0:  # 输入设备
            dev_name = info.get('name').lower()
            if name_substring.lower() in dev_name:
                return i
    return None

def main():
    # 1) 创建监听 Socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT_OUT))
    server_socket.listen(5)
    print(f"[server_out] Listening on port {PORT_OUT}, waiting for client...")

    # 2) 初始化 PyAudio
    p = pyaudio.PyAudio()
    # 假设 Zoom/Teams 扬声器选 "BlackHole 2ch"；这里录制它
    input_index = find_device_index_by_substring(p, "blackhole 2ch")
    if input_index is None:
        input_index = find_device_index_by_substring(p, "blackhole 16ch")
    print(f"[server_out] Using input device index={input_index}")

    while True:
        print("[server_out] Accepting new client...")
        conn, addr = server_socket.accept()
        print(f"[server_out] Client connected from: {addr}")

        # 打开录音流
        stream_in = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=input_index
        )

        try:
            while True:
                # 使用 exception_on_overflow=False 避免遇到 overflow 就抛异常
                data = stream_in.read(CHUNK, exception_on_overflow=False)
                conn.sendall(data)
        except Exception as e:
            print("[server_out] Exception:", e)
        finally:
            stream_in.stop_stream()
            stream_in.close()
            conn.close()
            print("[server_out] Connection closed, wait for next client.")

    p.terminate()
    server_socket.close()

if __name__ == "__main__":
    main()
