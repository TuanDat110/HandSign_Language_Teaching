from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
import cv2
import torch
from ultralytics import YOLO
import numpy as np
import websocket
# Khởi tạo FastAPI
app = FastAPI()


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = YOLO("D:/install/AI/Code/Project/yolo/V8/Yolov8/runs/detect/train/weights/best.pt")
model.to(device)  # Chạy trên GPU


templates = Jinja2Templates(directory="templates")

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.websocket("/ws")
async def get_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            contents = await websocket.receive_bytes()
            arr = np.frombuffer(contents, np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)

            if frame is None:
                print("Lỗi khi giải mã ảnh!")
                continue
            # Resize ảnh trước khi đưa vào model
            frame = cv2.resize(frame, (640, 480))

            # Dự đoán
            results = model.predict(frame, device=device)
            frame = results[0].plot()
            # 🚀 Xử lý YOLO (nếu cần)
            # results = model.predict(frame, device=device)
            # frame = results[0].plot()  # Nếu YOLO, vẽ kết quả lên frame

            # Encode ảnh và gửi qua WebSocket
            _, buffer = cv2.imencode('.jpg', frame)
            await websocket.send_bytes(buffer.tobytes())

            # Giảm tải CPU/GPU
            await asyncio.sleep(0.02)

    except WebSocketDisconnect:
        print("Client disconnected")
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8001)