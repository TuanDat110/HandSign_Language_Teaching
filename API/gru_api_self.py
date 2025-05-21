from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
import cv2
import torch
from ultralytics import YOLO
import numpy as np
from decimal import Decimal
from collections import deque
import mediapipe as mp  
import time
from mp import *
import os
os.environ["OMP_NUM_THREADS"] = "4"
# Khởi tạo FastAPI
app = FastAPI()
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Tải model YOLO chỉ một lần
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#khai báo các classes
class_names = np.array( ["aw","ee","oo","sac", "hoi","nang","nothing","aa","ow","uw", "nga","huyen"])

# log_dir = os.path.join('Logs_file\Logs_8_5\Logs_GRU_8_5')
# tb_callback = TensorBoard(log_dir=log_dir)
# cấu trúc model LSTM
'''
STEP 3: CREATE MODEL CLASS
'''
import torch
import torch.nn as nn

class GRUModel(nn.Module):
    def __init__(self, input_size, hidden_size1, hidden_size2, num_classes):
        super(GRUModel, self).__init__()
        
        # GRU layer 1
        self.gru1 = nn.GRU(input_size=input_size, hidden_size=hidden_size1, 
                          batch_first=True)
        self.dropout1 = nn.Dropout(p=0.2)
        
        # GRU layer 2
        self.gru2 = nn.GRU(input_size=hidden_size1, hidden_size=hidden_size2, 
                          batch_first=True)
        self.dropout2 = nn.Dropout(p=0.2)
        
        # Flatten (handled in forward)
        # Dense layer
        self.fc = nn.Linear(hidden_size2 * 30, num_classes)  # 30 là seq_len
        
        # Softmax không cần khai báo riêng vì thường xử lý trong loss function
        
    def forward(self, x):
        # GRU layer 1
        out, _ = self.gru1(x)  # out: [batch_size, seq_len, hidden_size1]
        out = self.dropout1(out)
        
        # GRU layer 2
        out, _ = self.gru2(out)  # out: [batch_size, seq_len, hidden_size2]
        out = self.dropout2(out)
        
        # Flatten
        out = out.reshape(out.size(0), -1)  # [batch_size, seq_len * hidden_size2]
        
        # Dense layer
        out = self.fc(out)  # [batch_size, num_classes]
        
        return out  # Softmax sẽ được áp dụng trong loss (CrossEntropyLoss)
# Khởi tạo mô hình
input_size = 63    # Số đặc trưng tại mỗi timestep
hidden_size1 = 256 # Kích thước hidden state của GRU đầu tiên
hidden_size2 = 128 # Kích thước hidden state của GRU thứ hai
num_classes = class_names.shape[0]  # Số lớp đầu ra (từ biến actions_train)

model = GRUModel(input_size, hidden_size1, hidden_size2, num_classes)  
#compile model 
# max_epoch = 120
# LR = 0.001
# criterion = nn.CrossEntropyLoss()
# optimizer = torch.optim.Adam(model.parameters(), lr=LR)
torch.manual_seed(1)
'''
STEP 4: INSTANTIATE MODEL CLASS
'''




#######################
#  USE GPU FOR MODEL  #
#######################
    
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model.to(device)

# Load trọng số mô hình từ file đã lưu
model.load_state_dict(torch.load('D:/install/AI/Code/Project/GRU_MODEL/gru_model.pth'))

# Đặt mô hình vào chế độ đánh giá (evaluation mode)
model.eval()

# Thông số đầu vào
SEQUENCE_LENGTH = 30
PREDICTION_THRESHOLD = 0.5  # Ngưỡng dự đoán 50%


templates = Jinja2Templates(directory="templates")

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Hàm đọc camera async
async def read_camera():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, cap.read)

@app.websocket("/ws")
async def get_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            success, frame = await read_camera()
            if not success:
                break
                        # Hàng đợi lưu trữ frames
            frames_queue = deque(maxlen=SEQUENCE_LENGTH)

            # Trạng thái của chương trình
            state = "start"
            start_time = time.time()
            predicted_class = ""
            prediction_score = 0.0
            with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        print("❌ Không thể đọc frame từ webcam!")
                        break

                    current_time = time.time()

                    if state == "start":
                        # 🟢 Hiển thị thông báo thu thập trong 2 giây
                        if current_time - start_time < 2:
                            cv2.putText(frame, "STARTING COLLECTION", (50, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3, cv2.LINE_AA)
                        else:
                            state = "collect"
                            frames_queue.clear()  # Xóa dữ liệu cũ

                    elif state == "collect":
                        # 🟡 Thu thập SEQUENCE_LENGTH frames
                    
                        frame, results = mediapipe_detection(frame, holistic)

                        # Draw landmarks
                        draw_styled_landmarks(frame, results)

                        # 2. Prediction logic
                        keypoints = extract_keypoints(results)
                        frames_queue.append(keypoints)
                        # count.append(keypoints)
                        # frames_queue.append(frame_resized)

                        cv2.putText(frame, f"Collecting: {len(frames_queue)}/{SEQUENCE_LENGTH}", (30, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

                        if len(frames_queue) == SEQUENCE_LENGTH:
                            state = "predict"
                            print(len(frames_queue))

                    elif state == "predict":
                        # 🔴 Dự đoán
                        sequence_tensor = np.expand_dims(frames_queue, axis=0)  # Thêm chiều batch
                        sequence_tensor = torch.tensor(sequence_tensor, dtype=torch.float32).to(device)
                        with torch.no_grad():
                # Dự đoán
                                    res_tensor = model(sequence_tensor)  # Gọi mô hình trực tiếp
                                    res = torch.softmax(res_tensor[0], dim=-1).cpu().numpy()  # Chuyển logits thành xác suất
                                    predicted_index = np.argmax(res)
                                    prediction_score = res[predicted_index]
                                    print(prediction_score)

                        if prediction_score >= PREDICTION_THRESHOLD:
                            predicted_class = class_names[predicted_index] if predicted_index < len(class_names) else "Không xác định"
                        else:
                            predicted_class = "Không xác định"

                        start_time = current_time  # Cập nhật thời gian để hiển thị kết quả
                        state = "show_result"

                    elif state == "show_result":
                        # 🟠 Hiển thị kết quả trong 2 giây nếu độ tin cậy >= ngưỡng
                        if prediction_score >= PREDICTION_THRESHOLD:
                            cv2.putText(frame, f"Class: {predicted_class}", (30, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                            cv2.putText(frame, f"Score: {round(Decimal(prediction_score * 100), 2)}%", (30, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                        else:
                            cv2.putText(frame, "Prediction confidence below threshold", (30, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                        if current_time - start_time >= 2:
                            state = "start"  # Quay lại thu thập
                    # Encode ảnh và gửi qua WebSocket
                    _, buffer = cv2.imencode('.jpg', frame)
                    await websocket.send_bytes(buffer.tobytes())

                    # Giảm tải CPU/GPU
                    await asyncio.sleep(0.01)  # Có thể chỉnh 0.01 - 0.05 tùy tốc độ cần thiết

    except (WebSocketDisconnect, ConnectionClosed):
        print("Client disconnected")

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8001)
