import cv2
import asyncio
import numpy as np
import mediapipe as mp
import websockets
from collections import deque
import time

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
SEQUENCE_LENGTH = 30
PREDICTION_THRESHOLD = 0.5
class_names = np.array(["aw", "ee", "oo", "sac", "hoi", "nang", "nothing", "aa", "ow", "uw", "nga", "huyen"])

# Hàm đọc camera async
async def read_camera():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, camera.read)

# Hàm trích xuất keypoints (giả sử từ mp.py)
def extract_keypoints(results):
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return rh

# Hàm phát hiện MediaPipe (giả sử từ mp.py)
def mediapipe_detection(frame, model):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model.process(frame_rgb)
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    return frame_bgr, results

# Hàm vẽ landmarks (giả sử từ mp.py)
def draw_styled_landmarks(frame, results):
    mp_drawing = mp.solutions.drawing_utils
    mp_holistic = mp.solutions.holistic
    if results.right_hand_landmarks:
        mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

async def send_video():
    url = 'ws://127.0.0.1:8000/ws'
    async with websockets.connect(url) as websocket:
        try:
            frames_queue = deque(maxlen=SEQUENCE_LENGTH)
            state = "start"
            start_time = time.time()
            predicted_class = ""
            prediction_score = 0.0

            with mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
                while True:
                    ret, frame = await read_camera()
                    if not ret:
                        print("Không thể đọc camera")
                        break

                    current_time = time.time()

                    if state == "start":
                        if current_time - start_time < 2:
                            cv2.putText(frame, "STARTING COLLECTION", (50, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3, cv2.LINE_AA)
                        else:
                            state = "collect"
                            frames_queue.clear()

                    elif state == "collect":
                        frame, results = mediapipe_detection(frame, holistic)
                        draw_styled_landmarks(frame, results)
                        keypoints = extract_keypoints(results)
                        frames_queue.append(keypoints)

                        cv2.putText(frame, f"Collecting: {len(frames_queue)}/{SEQUENCE_LENGTH}", (30, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

                        if len(frames_queue) == SEQUENCE_LENGTH:
                            # Chuyển deque thành mảng NumPy
                            frames_array = np.array(frames_queue, dtype=np.float32)  # Shape: (30, 63)
                            await websocket.send(frames_array.tobytes())  # Gửi 7560 bytes
                            print("📤 Sent keypoints")

                            # Nhận kết quả từ server
                            data = await websocket.recv()
                            arr = np.frombuffer(data, dtype=np.float32)
                            predicted_index = int(arr[0])
                            prediction_score = arr[1]
                            predicted_class = class_names[predicted_index]

                            start_time = current_time
                            state = "show_result"

                    elif state == "show_result":
                        if prediction_score >= PREDICTION_THRESHOLD:
                            cv2.putText(frame, f"Class: {predicted_class}", (30, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                            cv2.putText(frame, f"Score: {prediction_score:.2%}", (30, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                        else:
                            cv2.putText(frame, "Prediction confidence below threshold", (30, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                        if current_time - start_time >= 2:
                            state = "start"

                    # Hiển thị frame liên tục
                    cv2.imshow("Processed Frame", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    await asyncio.sleep(0.03)  # Duy trì ~33 FPS

        except websockets.exceptions.ConnectionClosed:
            print("WebSocket bị đóng")
        finally:
            camera.release()
            cv2.destroyAllWindows()

asyncio.run(send_video())