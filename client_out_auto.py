# client_out_auto.py
import socket
import pyaudio
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

SERVER_IP = "192.168.31.244"  # 替换成服务器( Mac )的IP
PORT_OUT = 50008           # 与 server_out_auto.py 对应端口
RECONNECT_DELAY = 5

def main():
    p = pyaudio.PyAudio()

    while True:
        print("[client_out] 尝试连接服务器...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((SERVER_IP, PORT_OUT))
            print("[client_out] 连接成功.")

            # 打开播放流
            stream_out = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK
            )

            try:
                while True:
                    data = sock.recv(CHUNK)
                    if not data:
                        print("[client_out] 服务器断开连接.")
                        break
                    stream_out.write(data)
            except Exception as e:
                print("[client_out] 接收/播放异常:", e)
            finally:
                stream_out.stop_stream()
                stream_out.close()

        except Exception as e:
            print("[client_out] 连接失败/异常:", e)

        # 连接断开或异常 -> 关闭并重连
        try:
            sock.close()
        except:
            pass

        print(f"[client_out] {RECONNECT_DELAY}s 后重连...")
        time.sleep(RECONNECT_DELAY)

    p.terminate()

if __name__ == "__main__":
    main()
