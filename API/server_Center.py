import socket
import struct
import cv2
import numpy as np
import mediapipe as mp
import torch
import torch.nn as nn
from collections import deque
import time
from ultralytics import YOLO
# Debug print to confirm script start
print("Script started")

# Server configuration
HOST = '0.0.0.0'
PORT = 5000

# MediaPipe setup
mp_holistic = mp.solutions.holistic
model_yolo = YOLO("D:/install/AI/Code/Project/yolo/V8/Yolov8/runs/detect/train/weights/best.pt")
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model_yolo.to(device)
# GRU model setup
class_names = np.array( ["aw","ee","ow","sac", "hoi","nang","nothing","aa","oo","uw", "nga","huyen"])
input_size = 63
hidden_size1 = 256
hidden_size2 = 128
num_classes = len(class_names)
SEQUENCE_LENGTH = 30
PREDICTION_THRESHOLD = 0.5
# # Define GRUModel class
# class GRUModel(nn.Module):
#     def __init__(self, input_size, hidden_size1, hidden_size2, num_classes):
#         super(GRUModel, self).__init__()
        
#         # GRU layer 1
#         self.gru1 = nn.GRU(input_size=input_size, hidden_size=hidden_size1, 
#                           batch_first=True)
#         self.dropout1 = nn.Dropout(p=0.2)
        
#         # GRU layer 2
#         self.gru2 = nn.GRU(input_size=hidden_size1, hidden_size=hidden_size2, 
#                           batch_first=True)
#         self.dropout2 = nn.Dropout(p=0.2)
        
#         self.fc = nn.Linear(hidden_size2 * 30, num_classes)  # 30 là seq_len
        
#     def forward(self, x):
#         # GRU layer 1
#         out, _ = self.gru1(x)  # out: [batch_size, seq_len, hidden_size1]
#         out = self.dropout1(out)
        
#         # GRU layer 2
#         out, _ = self.gru2(out)  # out: [batch_size, seq_len, hidden_size2]
#         out = self.dropout2(out)
        
#         # Flatten
#         out = out.reshape(out.size(0), -1)  # [batch_size, seq_len * hidden_size2]
        
#         # Dense layer
#         out = self.fc(out)  # [batch_size, num_classes]
        
#         return out  # Softmax sẽ được áp dụng in the prediction step

# # Initialize GRU model
try:
    model = torch.jit.load('D:/install/AI/Code/Project/GRU_MODEL/gru.pt', map_location=device)
    model.eval()
    print("Model loaded successfully")
except Exception as e:
    print(f"Failed to load model: {e}")
    exit(1)

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def extract_keypoints(results):
    if results.right_hand_landmarks:
        return np.array([[lm.x, lm.y, lm.z] for lm in results.right_hand_landmarks.landmark]).flatten()
    return np.zeros(21 * 3)

def send_video(img):
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = holistic.process(frame_rgb)
        keypoints = extract_keypoints(results)
    return keypoints.tolist()

def model_AI(list_frame):
    sequence = np.array(list_frame).reshape(1, SEQUENCE_LENGTH, input_size)  # Shape: (1, 30, 63)
    sequence_tensor = torch.tensor(sequence, dtype=torch.float32).to(device)
    
    with torch.no_grad():
        logits = model(sequence_tensor)
        probabilities = torch.softmax(logits, dim=-1).cpu().numpy()[0]
        predicted_index = np.argmax(probabilities)
        prediction_score = probabilities[predicted_index]
        
        if prediction_score >= PREDICTION_THRESHOLD:
            return class_names[predicted_index]
        return "Không xác định"

def start_server():
    print("Starting server...")
    check = 0
    idx = 0
    questions = ["A", "aw", "B", "aa", "C", "ee", "D", "uw", "E", "huyen"]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Server listening at {HOST}:{PORT}")
        listframe = []
        while True:
            try:
                conn, addr = s.accept()
                print(f"Connected by {addr}")
                
                with conn:
                    starrTime = time.time()
                    cnt = 0
                    while True:
                        # Receive header
                        header = recvall(conn, 4)
                        if not header:
                            print("Client disconnected.")
                            break
                            
                        img_size = struct.unpack('>I', header)[0]
                        
                        # Receive image data
                        img_data = recvall(conn, img_size)
                        if img_data is None:
                            print("Client disconnected.")
                            break
                            
                        # Decode image
                        np_arr = np.frombuffer(img_data, dtype=np.uint8)
                        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                        if img is None:
                            print("Failed to decode image.")
                            continue
                        if(check == 1):
                            # Extract keypoints
                            print('gru')
                            keypoints = send_video(img)
                            listframe.append(keypoints)
                            
                            # Make prediction when buffer is full
                            prediction = "Waiting for enough frames"
                            print(cnt)
                            cnt+=1
                            if len(listframe) == SEQUENCE_LENGTH:
                                prediction = model_AI(list(listframe))
                                listframe = []
                                endTime = time.time()
                                resTime = endTime - starrTime
                                print(f"-------------------------------------------------------------{resTime}")
                                if prediction == questions[idx]:
                                    check = 0
                                    idx += 1
                            response_bytes = prediction.encode('utf-8')
                            resp_header = struct.pack('>I', len(response_bytes))
                            conn.sendall(resp_header + response_bytes)
                            
                        elif(check == 0):
                            print("yolo")
                            frame = cv2.resize(img, (640, 480))

                            results = model_yolo(frame, device = device)
                            output = results[0]
                            class_ids = output.boxes.cls.tolist() if output.boxes is not None else []

                            class_names = [model_yolo.names[int(cls_id)] for cls_id in class_ids]
                            
                            response_string = ','.join(class_names)
                            print(response_string)
                            response_bytes = response_string.encode('utf-8')
                            resp_header = struct.pack('>I', len(response_bytes))
                            conn.sendall(resp_header + response_bytes)
                            if response_string == questions[idx]:
                                check = 1
                                idx += 1
                            
                            
            except Exception as e:
                print(f"Error: {e}")
                continue
            finally:
                conn.close()

if __name__ == "__main__":
    start_server()