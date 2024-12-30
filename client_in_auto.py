# client_in_auto.py
import socket
import pyaudio
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

SERVER_IP = "192.168.31.244"  # 替换成服务器( Mac )的IP
PORT_IN = 50007            # 与 server_in_auto.py 的端口匹配
RECONNECT_DELAY = 5        # 断线后多少秒再重试连接

def main():
    p = pyaudio.PyAudio()

    while True:
        print("[client_in] 尝试连接服务器...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((SERVER_IP, PORT_IN))
            print("[client_in] 连接成功.")

            # 打开麦克风录音流
            stream_in = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )

            try:
                while True:
                    data = stream_in.read(CHUNK)
                    sock.sendall(data)
            except Exception as e:
                print("[client_in] 发送/录音异常:", e)
            finally:
                stream_in.stop_stream()
                stream_in.close()

        except Exception as e:
            print("[client_in] 连接失败/异常:", e)

        # 若执行到这里说明连接断开或异常 -> 关闭并重连
        try:
            sock.close()
        except:
            pass

        print(f"[client_in] {RECONNECT_DELAY}s 后重连...")
        time.sleep(RECONNECT_DELAY)

    # p.terminate() 理论上不会执行到这里
    p.terminate()

if __name__ == "__main__":
    main()
