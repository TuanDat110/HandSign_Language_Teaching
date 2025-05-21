import cv2
import asyncio
import websockets
import numpy as np

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Hàm đọc camera async
async def read_camera():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, camera.read)

async def send_video():
    url = 'ws://127.0.0.1:8001/ws'
    async with websockets.connect(url) as websocket:
        try:
            while True:
                ret, frame = await read_camera()
                if not ret:
                    print("Không thể đọc camera")
                    break

                # Encode frame thành JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                await websocket.send(buffer.tobytes())  # Gửi ảnh lên server
                print("📤 Sent frame")

                # 🛑 **Thêm phần nhận dữ liệu từ server**
                data = await websocket.recv()
                arr = np.frombuffer(data, np.uint8)
                processed_frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

                if processed_frame is not None:
                    cv2.imshow("Processed Frame", processed_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except websockets.exceptions.ConnectionClosed:
            print("WebSocket bị đóng")
        finally:
            camera.release()
            cv2.destroyAllWindows()

asyncio.run(send_video())
