import cv2
import numpy as np
import os
import torch
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from matplotlib import pyplot as plt
import time
import mediapipe as mp
import tensorflow as tf
# of object_detection
# from object_detection.utils import config_util
# from object_detection.protos import pipeline_pb2
from google.protobuf import text_format
import os
# from object_detection.utils import label_map_util
# from object_detection.utils import visualization_utils as viz_utils
# from object_detection.builders import model_builder
import six
import sys
# import serial
# from serial import Serial
import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPixmap,QImage
from PyQt5.QtWidgets import QApplication, QMainWindow,QFileDialog, QMessageBox, QLabel
from Giao_dien_test import Ui_MainWindow
from PyQt5 import QtWidgets
from Sub_page_5_nckh import Ui_Form
import speech_recognition
from decimal import Decimal
from collections import deque
from Chuyen_co_dau_thanh_khong_dau import ma_hoa_telex



#Object Detection 
# model_yolo = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5/best_5M_150_epochs.pt', autoshape=True, verbose=True, device=None)
from ultralytics import YOLO
model_yolo = YOLO('D:/install/AI/Code/Project/yolo/V8/Yolov8/runs/detect/train/weights/best.pt')
model_yolo.conf = 0.5


# ACTION RECOGNITION
mp_holistic = mp.solutions.holistic # Holistic model
mp_drawing = mp.solutions.drawing_utils # Drawing utilities
def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # COLOR CONVERSION BGR 2 RGB
    image.flags.writeable = False                  # Image is no longer writeable
    results = model.process(image)                 # Make prediction
    image.flags.writeable = True                   # Image is now writeable 
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # COLOR COVERSION RGB 2 BGR
    return image, results
def draw_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS) # Draw right hand connections
def draw_styled_landmarks(image, results):
    # Draw right hand connections  
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                             mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4), 
                             mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                             )
def extract_keypoints(results):
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([rh])

# Vẽ chữ stop lên màn hình
def draw_class_on_image(label,img):
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (120,200)
    fontScale = 5
    fontColor = (20,20,200)
    thichkness=8
    lineType=2
    cv2.putText(img,label,
               bottomLeftCornerOfText,
               font,
               fontScale,
               fontColor,
               thichkness,
               lineType)
    return img

#khai báo các classes
actions = np.array([  "aw","ee","ow","sac", "hoi","nang","nothing","aa","oo","uw", "nga","huyen" ])
# Danh sách tên class
class_names = ["aw","ee","ow","sac", "hoi","nang","nothing","aa","oo","uw", "nga","huyen"]
label_map = {label:num for num, label in enumerate(actions)}
# log_dir = os.path.join('Logs_file\Logs_8_5\Logs_GRU_8_5')
# tb_callback = TensorBoard(log_dir=log_dir)
# cấu trúc model LSTM
'''
STEP 3: CREATE MODEL CLASS
'''
import torch
import torch.nn as nn

# Load model đã trace
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = torch.jit.load("D:/install/AI/Code/Project/GRU_MODEL/gru.pt", map_location=device)
model.eval()  # Đặt chế độ eval để inference

# serialcom = serial.Serial('COM5',9600) #mở serial ở cổng số 3, Rbaud = 9600
# serialcom.timeout = 1

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self)
        self.trangthai = False
        self.object_detection = True
        self.action_recognition = False
        self.cau_hoi_hien_tai = 0
        self.TEXT = []
        self.uic.label_10.setAlignment(QtCore.Qt.AlignCenter)
        # khai bao nut nhan
            #các nút chọn page chế dộ
        self.uic.pushButton.clicked.connect(self.page_chon_che_do)
        self.uic.pushButton_3.clicked.connect(self.page_hoc_chu) 
        self.uic.pushButton_4.clicked.connect(self.page_kiem_tra)
        self.uic.pushButton_5.clicked.connect(self.page_phien_dich)
        
            #các home khác nhau
        self.uic.pushButton_13.clicked.connect(self.page_chon_che_do) #nút home page học chữ
        self.uic.pushButton_54.clicked.connect(self.page_chon_che_do)#nút home page phiên dịch

        self.uic.pushButton_32.clicked.connect(self.stop_video_in_page_chon_che_do) #nút home page kiểm tra

        self.uic.pushButton_52.clicked.connect(self.open_sub_page_5)  #nút thu giọng nói
        self.uic.pushButton_53.clicked.connect(self.close_sub_page_5) #nút mã hóa và gửi dữ liệu cho arduino

        #Khai báo chữ cái
        self.uic.pushButton_2.clicked.connect(self.Gui_chu_A)
        self.uic.pushButton_33.clicked.connect(self.Gui_chu_AW)
        self.uic.pushButton_41.clicked.connect(self.Gui_chu_AA)
        self.uic.pushButton_7.clicked.connect(self.Gui_chu_B)
        self.uic.pushButton_8.clicked.connect(self.Gui_chu_C)
        self.uic.pushButton_6.clicked.connect(self.Gui_chu_D)
        self.uic.pushButton_42.clicked.connect(self.Gui_chu_DD)
        self.uic.pushButton_9.clicked.connect(self.Gui_chu_E)
        self.uic.pushButton_43.clicked.connect(self.Gui_chu_EE)
        self.uic.pushButton_10.clicked.connect(self.Gui_chu_G)
        self.uic.pushButton_11.clicked.connect(self.Gui_chu_H)
        self.uic.pushButton_12.clicked.connect(self.Gui_chu_I)
        self.uic.pushButton_15.clicked.connect(self.Gui_chu_K)
        self.uic.pushButton_19.clicked.connect(self.Gui_chu_L)
        self.uic.pushButton_17.clicked.connect(self.Gui_chu_M)
        self.uic.pushButton_20.clicked.connect(self.Gui_chu_N)
        self.uic.pushButton_18.clicked.connect(self.Gui_chu_O)
        self.uic.pushButton_44.clicked.connect(self.Gui_chu_OO)
        self.uic.pushButton_45.clicked.connect(self.Gui_chu_OW)
        self.uic.pushButton_21.clicked.connect(self.Gui_chu_P)
        self.uic.pushButton_16.clicked.connect(self.Gui_chu_Q)
        self.uic.pushButton_14.clicked.connect(self.Gui_chu_R)
        self.uic.pushButton_38.clicked.connect(self.Gui_chu_S)
        self.uic.pushButton_22.clicked.connect(self.Gui_chu_T)
        self.uic.pushButton_31.clicked.connect(self.Gui_chu_U)
        self.uic.pushButton_46.clicked.connect(self.Gui_chu_UW)
        self.uic.pushButton_28.clicked.connect(self.Gui_chu_V)
        self.uic.pushButton_34.clicked.connect(self.Gui_chu_X)
        self.uic.pushButton_27.clicked.connect(self.Gui_chu_Y)
        self.uic.pushButton_47.clicked.connect(self.Gui_chu_sac)
        self.uic.pushButton_48.clicked.connect(self.Gui_chu_huyen)
        self.uic.pushButton_49.clicked.connect(self.Gui_chu_hoi)
        self.uic.pushButton_50.clicked.connect(self.Gui_chu_nga)
        self.uic.pushButton_51.clicked.connect(self.Gui_chu_nang)

        #khai bao cac chu so
        self.uic.pushButton_36.clicked.connect(self.Gui_so_0)
        self.uic.pushButton_25.clicked.connect(self.Gui_so_1)
        self.uic.pushButton_29.clicked.connect(self.Gui_so_2)
        self.uic.pushButton_30.clicked.connect(self.Gui_so_3)
        self.uic.pushButton_23.clicked.connect(self.Gui_so_4)
        self.uic.pushButton_26.clicked.connect(self.Gui_so_5)
        self.uic.pushButton_35.clicked.connect(self.Gui_so_6)
        self.uic.pushButton_37.clicked.connect(self.Gui_so_7)
        self.uic.pushButton_40.clicked.connect(self.Gui_so_8)
        self.uic.pushButton_39.clicked.connect(self.Gui_so_9)


        #page 4
        self.uic.pushButton_24.clicked.connect(self.Chuong_trinh_nhan_dien) #mở đề kiểm tra
        self.thread = {} #ban đầu ko có luồng nào chạy riêng 
        self.label_ket_thuc = QLabel("Kết thúc kiểm tra", self)
        self.label_ket_thuc.setStyleSheet("font-size: 30px; color: red; background: transparent;")
        self.label_ket_thuc.adjustSize()
        self.label_ket_thuc.move(220, 350)
        self.label_ket_thuc.raise_()
        self.label_ket_thuc.hide()
        
    #Hàm thông báo thoát khỏi giao diện 
    def closeEvent(self, event):
        if self.trangthai == True:
            self.stop_capture_video()
            self.trangthai = False
        reply = QMessageBox.question(self, 'Thoát chương trình', 'Bạn có chắc chắn muốn thoát chương trình không?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            print('Thoát chương trình')
        else:
            event.ignore()
            
    # các lệnh mở page
    def page_chon_che_do(self):
        self.uic.stackedWidget.setCurrentWidget(self.uic.page_2)
    def page_hoc_chu(self):
        self.uic.stackedWidget.setCurrentWidget(self.uic.page_3)
    def page_kiem_tra(self):
        self.uic.stackedWidget.setCurrentWidget(self.uic.page_4)
    def page_phien_dich(self):
        self.uic.stackedWidget.setCurrentWidget(self.uic.page_5)
    def open_sub_page_5(self):
        # mở màn hình nhỏ hiện chữ đang ghi âm
        self.Second_window = QtWidgets.QMainWindow()
        self.uic1 = Ui_Form()
        self.uic1.setupUi(self.Second_window)
        self.Second_window.show()
        # chạy đa luồng, ghi âm
        self.thread[2] = speech_to_text(index=2)
        self.thread[2].start() #kích hoạt luồng 2 mở
        self.thread[2].signal_2.connect(self.show_text_from_speech) 
        so_nam="5"
        # serialcom.write(so_nam.encode())
    
    def show_text_from_speech(self, text):
        self.TEXT = ""
        self.TEXT = text
        if self.TEXT != "":
            print(self.TEXT)
            self.uic.label_10.setText(self.TEXT)
            self.Second_window.close()
            self.thread[2].stop()
            
    def close_sub_page_5(self):
        for char in self.TEXT :
            output= ma_hoa_telex(char)
            print (output[0])
            # serialcom.write(output[0].encode())
            time.sleep(4)
            if (len(output[1]) != 0 ):
                print (output[1])
                # serialcom.write(output[1].encode())
                time.sleep(4)
        
        
    

    #Gửi các chữ cái
    def Gui_chu_A(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/a_2.png'))
        gia_tri_serial = "a"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode()) #mã hóa dữ liệu và gửi đi
    def Gui_chu_AW(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/ă.png'))
        gia_tri_serial = "aw"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_AA(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/â_2.png'))
        gia_tri_serial = "aa"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_B(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/b.png'))
        gia_tri_serial = "b"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_C(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/c.png'))
        gia_tri_serial = "c"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_D(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/d.png'))
        gia_tri_serial = "d"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_DD(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/đ.png'))
        gia_tri_serial = "dd"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_E(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/e.png'))
        gia_tri_serial = "e"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_EE(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/ê.png'))
        gia_tri_serial = "ee"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_G(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/g.png'))
        gia_tri_serial = "g"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_H(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/h.png'))
        gia_tri_serial = "h"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_I(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/i.png'))
        gia_tri_serial = "i"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_K(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/k.png'))
        gia_tri_serial = "k"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_L(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/l.png'))
        gia_tri_serial = "l"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_M(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/m.png'))
        gia_tri_serial = "m"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_N(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/n.png'))
        gia_tri_serial = "n"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_O(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/o.png'))
        gia_tri_serial = "o"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_OW(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/ơ.png'))
        gia_tri_serial = "ow"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_OO(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/ô.png'))
        gia_tri_serial = "oo"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_P(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/p.png'))
        gia_tri_serial = "p"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_Q(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/q.png'))
        gia_tri_serial = "q"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_R(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/r.png'))
        gia_tri_serial = "r"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_S(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/s.png'))
        gia_tri_serial = "s"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_T(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/t.png'))
        gia_tri_serial = "t"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_U(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/u.png'))
        gia_tri_serial = "u"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_UW(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/ư.png'))
        gia_tri_serial = "uw"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_V(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/v.png'))
        gia_tri_serial = "v"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_X(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/x.png'))
        gia_tri_serial = "x"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_Y(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/y.png'))
        gia_tri_serial = "y"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_sac(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/dau sac.png'))
        gia_tri_serial = "sac"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_huyen(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/dau huyen.png'))
        gia_tri_serial = "huyen"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_hoi(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/dau hoi.png'))
        gia_tri_serial = "hoi"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_nga(self):
        self.uic.label_4.setPixmap(QPixmap('Chu_cai_va_so/dau ngã.png'))
        gia_tri_serial = "nga"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_chu_nang(self):
        self.uic.label_4.setPixmap(QPixmap("Chu_cai_va_so/dau nang.png"))
        gia_tri_serial = "nang"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())

    #Gửi các chữ số
    def Gui_so_0(self):
        self.uic.label_4.setPixmap(QPixmap("Chu_cai_va_so/0.png"))
        gia_tri_serial = "0"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_so_1(self):
        self.uic.label_4.setPixmap(QPixmap("Chu_cai_va_so/1.png"))
        gia_tri_serial = "1"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_so_2(self):
        self.uic.label_4.setPixmap(QPixmap("Chu_cai_va_so/2.png"))
        gia_tri_serial = "2"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_so_3(self):
        self.uic.label_4.setPixmap(QPixmap("Chu_cai_va_so/3.png"))
        gia_tri_serial = "3"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_so_4(self):
        self.uic.label_4.setPixmap(QPixmap("Chu_cai_va_so/4.png"))
        gia_tri_serial = "4"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_so_5(self):
        self.uic.label_4.setPixmap(QPixmap("Chu_cai_va_so/5.png"))
        gia_tri_serial = "5"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_so_6(self):
        self.uic.label_4.setPixmap(QPixmap("Chu_cai_va_so/6.png"))
        gia_tri_serial = "6"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_so_7(self):
        self.uic.label_4.setPixmap(QPixmap("Chu_cai_va_so/7.png"))
        gia_tri_serial = "7"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_so_8(self):
        self.uic.label_4.setPixmap(QPixmap("Chu_cai_va_so/8.png"))
        gia_tri_serial = "8"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())
    def Gui_so_9(self):
        self.uic.label_4.setPixmap(QPixmap("Chu_cai_va_so/9.png"))
        gia_tri_serial = "9"
        print(gia_tri_serial)
        # serialcom.write(gia_tri_serial.encode())


    #page 4
    def stop_capture_video(self):
        self.thread[5].stop()
        print("stop 5 ảo")
        
        
    def stop_capture_video_1(self):
        self.thread[1].stop()
        print("dừng ctri 1")

    def stop_video_in_page_chon_che_do(self):
        self.uic.stackedWidget.setCurrentWidget(self.uic.page_2)
        if self.trangthai == True:        #nếu đang bật nhận diện 
            self.stop_capture_video()     #dừng luồng nhận diện
            self.trangthai = False #trạng thái bật nhận diện = false
                
    def Chuong_trinh_nhan_dien(self):  
        self.thread[1] = capture_video(index=0)
        self.thread[1].start()
        self.thread[1].signal.connect(self.show_wedcam) # tín hiệu gửi về là hình đã vẽ bouding box, đưa hình đó qua hàm show_webcam
        self.thread[1].signal_1.connect(self.phan_loai_so_tt)
        print("đang thực hiện detection")
    def Chuong_trinh_recognition(self):
        print("đang thực hiện recognition")
        if (self.object_detection == False) and (self.action_recognition == True):
            # self.thread[5] = mediapipe_capture(index=5)
            self.thread[5].start()
            self.thread[5].signal_5.connect(self.show_wedcam_2) # tín hiệu gửi về là hình có các keypoint, đưa hình đó qua hàm show_webcam
            self.thread[5].signal_5_1.connect(self.phan_loai_so_tt_2)
    
    # Hàm để chạy tính thời gian, nếu trả lời đúng sau 4s thì mới chuyển câu hỏi mới
    def Time_count (self):
        self.thread[4] = Timer_4s(index=4)
        self.thread[4].start()
        self.thread[4].signal_4.connect(self.chuyen_cau_hoi)

    def show_wedcam(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img) #convert lại hình sao cho phù hợp với chuẩn của pyqt5
        self.uic.label_7.setPixmap(qt_img)

    def phan_loai_so_tt(self, number_question):
        if number_question == 1:
            self.cau_hoi_hien_tai = 1
            self.Time_count()            
        if number_question == 2:
            self.cau_hoi_hien_tai = 2
            self.uic.label_12.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()
        if number_question == 3:
            self.cau_hoi_hien_tai = 3
            self.uic.label_13.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()
        if number_question == 4:
            self.cau_hoi_hien_tai = 4
            self.uic.label_14.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()
        if number_question == 5:
            self.cau_hoi_hien_tai = 5
            self.uic.label_15.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()
        if number_question == 6:
            self.cau_hoi_hien_tai = 6
            self.uic.label_16.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()     
        if number_question == 7:
            self.cau_hoi_hien_tai =7
            self.uic.label_17.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()            
        if number_question == 8:
            self.cau_hoi_hien_tai = 8
            self.uic.label_18.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()            
        if number_question == 9:
            self.cau_hoi_hien_tai = 9
            self.uic.label_19.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()            
        if number_question == 10:
            self.cau_hoi_hien_tai = 10
            self.uic.label_20.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()
        if number_question == 11:
            self.cau_hoi_hien_tai = 11
            self.uic.label_21.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()
        if number_question == 12:
            self.cau_hoi_hien_tai = 12
            self.uic.label_22.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()

    def show_wedcam_2(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img) #convert lại hình sao cho phù hợp với chuẩn của pyqt5
        self.uic.label_7.setPixmap(qt_img)   
    def phan_loai_so_tt_2(self, number_question):
        if number_question == 1:
            self.cau_hoi_hien_tai = 1
            self.Time_count()            
        if number_question == 2:
            self.cau_hoi_hien_tai = 2
            self.uic.label_12.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()
        if number_question == 3:
            self.cau_hoi_hien_tai = 3
            self.uic.label_13.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()
        if number_question == 4:
            self.cau_hoi_hien_tai = 4
            self.uic.label_14.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()
        if number_question == 5:
            self.cau_hoi_hien_tai = 5
            self.uic.label_15.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()
        if number_question == 6:
            self.cau_hoi_hien_tai = 6
            self.uic.label_16.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()     
        if number_question == 7:
            self.cau_hoi_hien_tai =7
            self.uic.label_17.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()            
        if number_question == 8:
            self.cau_hoi_hien_tai = 8
            self.uic.label_18.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()            
        if number_question == 9:
            self.cau_hoi_hien_tai = 9
            self.uic.label_19.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()            
        if number_question == 10:
            self.cau_hoi_hien_tai = 10
            self.uic.label_20.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()
        if number_question == 11:
            self.cau_hoi_hien_tai = 11
            self.uic.label_21.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()
        if number_question == 12:
            self.cau_hoi_hien_tai = 12
            self.uic.label_22.setPixmap(QPixmap("Chu_cai_va_so/Nut_T4_2.png"))
            self.cau_tra_loi_dung()
            self.Time_count()


    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(235, 178, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def convert_cv_qt_2(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(235, 178, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def cau_tra_loi_dung(self):
        self.thread[3] = show_video_tra_loi_dung(index=3)
        self.thread[3].start()
        self.thread[3].signal_3.connect(self.show_video)

    def show_video(self, cv_vid):
        """Updates the image_label with a new opencv image"""
        qt_vid = self.convert_video(cv_vid)
        self.uic.label_8.setPixmap(qt_vid)
    
    def show_video_2(self, cv_vid):
        """Updates the image_label with a new opencv image"""
        qt_vid = self.convert_video(cv_vid)
        self.uic.label_8.setPixmap(qt_vid)
    def show_video_3(self, cv_vid):
        """Updates the image_label with a new opencv image"""
        qt_vid = self.convert_video(cv_vid)
        self.uic.label_8.setPixmap(qt_vid)


    def convert_video(self, cv_vid):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_vid, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(1282, 462, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
    
    
    def chuyen_cau_hoi(self, number_signal):
        if (number_signal == 111) & (self.cau_hoi_hien_tai == 1) :            
            self.uic.label_6.setPixmap(QPixmap("Chu_cai_va_so/b.png"))
            self.thread[4].stop()
            
        elif (number_signal == 111):
            self.uic.label_6.clear()
        if (number_signal == 11) & (self.cau_hoi_hien_tai == 2):            
            self.uic.label_6.setPixmap(QPixmap("Chu_cai_va_so/đ.png"))
            self.thread[4].stop()
            self.thread[3].stop()
        if (number_signal == 11) & (self.cau_hoi_hien_tai == 3):            
            self.uic.label_6.setPixmap(QPixmap("Chu_cai_va_so/a_2.png"))
            self.thread[4].stop()
            self.thread[3].stop()
        if (number_signal == 11) & (self.cau_hoi_hien_tai == 4):            
            self.uic.label_6.setPixmap(QPixmap("Chu_cai_va_so/e.png"))
            self.thread[4].stop()
            self.thread[3].stop()
        if (number_signal == 11) & (self.cau_hoi_hien_tai == 5):            
            self.uic.label_6.setPixmap(QPixmap("Chu_cai_va_so/y.png"))
            self.thread[4].stop()
            self.thread[3].stop()
        if (number_signal == 11) & (self.cau_hoi_hien_tai == 6):        
            self.uic.label_6.setPixmap(QPixmap("Chu_cai_va_so/ă.png"))
            print("ă")
            self.thread[3].stop()
            #self.stop_capture_video_1() 

        #if (number_signal == 125) & (self.cau_hoi_hien_tai == 6):
            print("đã làm được bước này")   
            self.thread[4].stop()            
            print("đang thực hiện recognition")
            #self.thread[5] = mediapipe_capture(index=5)
            #self.thread[5].start()
            #self.thread[5].signal_5.connect(self.show_wedcam_2) # tín hiệu gửi về là hình có các keypoint, đưa hình đó qua hàm show_webcam
            #self.thread[5].signal_5_1.connect(self.phan_loai_so_tt_2)
            


        if (number_signal == 11) & (self.cau_hoi_hien_tai == 7):            
            self.uic.label_6.setPixmap(QPixmap("Chu_cai_va_so/ê.png"))
            print("ê")
            self.thread[4].stop()
        if (number_signal == 11) & (self.cau_hoi_hien_tai == 8):            
            self.uic.label_6.setPixmap(QPixmap("Chu_cai_va_so/ơ.png"))
            print("ơ")
            self.thread[4].stop()
        if (number_signal == 11) & (self.cau_hoi_hien_tai == 9):            
            self.uic.label_6.setPixmap(QPixmap("Chu_cai_va_so/dau sac.png"))
            print("sắc")
            self.thread[4].stop()
        if (number_signal == 11) & (self.cau_hoi_hien_tai == 10):            
            self.uic.label_6.setPixmap(QPixmap("Chu_cai_va_so/dau hoi.png"))
            print("hỏi")
            self.thread[4].stop() 
        if (number_signal == 11) & (self.cau_hoi_hien_tai == 11):            
            self.uic.label_6.setPixmap(QPixmap("Chu_cai_va_so/dau nang.png"))
            print("nặng")
            self.thread[4].stop()    
        if (number_signal == 11) & (self.cau_hoi_hien_tai == 12):            
            self.uic.label_6.clear()
            print("kết thúc kiểm tra")
            self.label_ket_thuc.show()
            QTimer.singleShot(3000, self.label_ket_thuc.hide)
            self.thread[4].stop()    
            # self.trangthai = False
            
class capture_video(QThread):
    signal = pyqtSignal(np.ndarray)
    signal_1 = pyqtSignal(int)
    def __init__(self, index):
        self.index = index
        self.Object = True
        self.Action = False
        print("start object detection", self.index)
        super(capture_video,self).__init__()

   
        
    def run(self):
        # model_yolo = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5/best.pt', autoshape=True, verbose=True, device=None)
        # model_yolo.conf = 0.5
        
        cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cau_hoi_ke_tiep=1
        cau_hoi_hien_tai = 0
        sequence = []
        sentence = []
        predictions = []
        threshold = 95
        count=[]
        score_numpy = 0 
        score_python =0
        noca = 0 #numbers of correct answer
        thresh_score = 50 #minimun score để xem đó là 1 nhận diện tốt 
        sentence_display = ""
        # Thông số đầu vào
        SEQUENCE_LENGTH = 30
        PREDICTION_THRESHOLD = 0.5  # Ngưỡng dự đoán 50%

            # Hàng đợi lưu trữ frames
        
        while (self.Object == True) & (self.Action == False):
            ret, frame = cap.read()
            detections = model_yolo(frame[..., ::-1])
            for det in detections:  # Duyệt qua từng Result trong list
                boxes = det.boxes  # Lấy thông tin bounding box
                if len(boxes) > 0:  # Nếu có phát hiện
                        for box in boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Lấy tọa độ
                            conf = box.conf[0].item()  # Độ tin cậy
                            clas = int(box.cls[0].item())  # Lớp
                            print(clas)
                            name = model_yolo.names[clas]  # Tên lớp
                            num_confidence = round(conf * 100)
                            if (clas == 0):
                                cv2.rectangle(frame,(x1,y1),(x2,y2), (56,87,249),5)
                                cv2.putText(frame, name, (x1+3,y1-10),cv2.FONT_HERSHEY_DUPLEX,1,(56,87,255),2)
                                cv2.putText(frame, str(num_confidence) + '%', (x1+40,y1-10),cv2.FONT_HERSHEY_SIMPLEX,1,(56,87,255),2)
                            if (clas == 1):
                                cv2.rectangle(frame,(x1,y1),(x2,y2), (75,150,238),5)
                                cv2.putText(frame, name, (x1+3,y1-10),cv2.FONT_HERSHEY_DUPLEX,1,(75,150,255),2)
                                cv2.putText(frame, str(num_confidence) + '%', (x1+40,y1-10),cv2.FONT_HERSHEY_SIMPLEX,1,(75,150,255),2)
                            if (clas == 22):
                                cv2.rectangle(frame,(x1,y1),(x2,y2), (94,211,244),5)
                                cv2.putText(frame, name, (x1+3,y1-10),cv2.FONT_HERSHEY_DUPLEX,1,(94,211,255),2)
                                cv2.putText(frame, str(num_confidence) + '%', (x1+40,y1-10),cv2.FONT_HERSHEY_SIMPLEX,1,(94,211,255),2)
                            if (clas == 5):
                                cv2.rectangle(frame,(x1,y1),(x2,y2), (40,201,150),5)
                                cv2.putText(frame, name, (x1+3,y1-10),cv2.FONT_HERSHEY_DUPLEX,1,(40,201,159),2)
                                cv2.putText(frame, str(num_confidence) + '%', (x1+40,y1-10),cv2.FONT_HERSHEY_SIMPLEX,1,(40,201,159),2)
                            if (clas == 4):
                                cv2.rectangle(frame,(x1,y1),(x2,y2), (224,217,174),5)
                                cv2.putText(frame, name, (x1+3,y1-10),cv2.FONT_HERSHEY_DUPLEX,1,(224,217,179),2)
                                cv2.putText(frame, str(num_confidence) + '%', (x1+40,y1-10),cv2.FONT_HERSHEY_SIMPLEX,1,(224,217,179),2)
                            # Câu lệnh để đọc kết quả, đọc 10 lần nếu chỉ số tin cậy 10 lần đều cùng trên 1 mức nào đó thì công nhận đó là kết quả đúng
                            if (name == "B") & (num_confidence > thresh_score) & (cau_hoi_hien_tai == 1)  :
                                noca = noca+1
                                if (noca == 10):
                                    print("ban da tra loi dung chữ B")
                                    noca = 0
                                    cau_hoi_ke_tiep = 2                
                            if (name == "DD") & (num_confidence > thresh_score) & (cau_hoi_hien_tai == 2)  :
                                noca = noca+1
                                if (noca == 10):
                                    print("ban da tra loi dung chữ đ")
                                    noca = 0
                                    cau_hoi_ke_tiep = 3    
                            if (name == "A") & (num_confidence > thresh_score) & (cau_hoi_hien_tai == 3)  :
                                noca = noca+1
                                if (noca == 10):
                                    print("ban da tra loi dung chữ A")
                                    noca = 0
                                    cau_hoi_ke_tiep = 4    
                            if (name == "E") & (num_confidence > thresh_score) & (cau_hoi_hien_tai == 4)  :
                                noca = noca+1
                                if (noca == 10):
                                    print("ban da tra loi dung chữ E")
                                    noca = 0
                                    cau_hoi_ke_tiep = 5    
                            if (name == "Y") & (num_confidence > thresh_score) & (cau_hoi_hien_tai == 5)  :
                                noca = noca+1
                                if (noca == 2):
                                    print("ban da tra loi dung chữ Y")
                                    noca = 0
                                    cau_hoi_ke_tiep = 6
                                    self.Action = True
                                    self.Object = False    
            if ret:
                self.signal.emit(frame)
            if cau_hoi_ke_tiep != cau_hoi_hien_tai :
                cau_hoi_hien_tai = cau_hoi_ke_tiep
                self.signal_1.emit(cau_hoi_hien_tai)
            #print('fps', 1/(time.time()-t))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
        
        while (self.Object == False) & (self.Action == True):
            frames_queue = deque(maxlen=SEQUENCE_LENGTH)
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
                            if (actions[np.argmax(res)] == "aw") & (cau_hoi_hien_tai == 6):
                                        predicted_class = class_names[predicted_index] if predicted_index < len(class_names) else "Không xác định"
                                        cau_hoi_ke_tiep= 7

                            if (actions[np.argmax(res)] == "ee") & (cau_hoi_hien_tai == 7):
                                predicted_class = class_names[predicted_index] if predicted_index < len(class_names) else "Không xác định"
                                cau_hoi_ke_tiep= 8
                            if (actions[np.argmax(res)] == "ow") & (cau_hoi_hien_tai == 8):
                                predicted_class = class_names[predicted_index] if predicted_index < len(class_names) else "Không xác định"
                                cau_hoi_ke_tiep= 9
                            if (actions[np.argmax(res)] == "sac") & (cau_hoi_hien_tai == 9):
                                predicted_class = class_names[predicted_index] if predicted_index < len(class_names) else "Không xác định"
                                cau_hoi_ke_tiep= 10
                            if (actions[np.argmax(res)] == "hoi") & (cau_hoi_hien_tai == 10):
                                predicted_class = class_names[predicted_index] if predicted_index < len(class_names) else "Không xác định"
                                cau_hoi_ke_tiep= 11
                            if (actions[np.argmax(res)] == "nang") & (cau_hoi_hien_tai == 11):
                                predicted_class = class_names[predicted_index] if predicted_index < len(class_names) else "Không xác định"
                                cau_hoi_ke_tiep= 12
                            else:
                                predicted_class = class_names[predicted_index]
                            

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

                    # # Hiển thị khung hình
                    # cv2.imshow("Real-time Testing", frame)


                        

                            
  
                    if ret:
                        self.signal.emit(frame)
                    if cau_hoi_ke_tiep != cau_hoi_hien_tai :
                        cau_hoi_hien_tai = cau_hoi_ke_tiep
                        self.signal_1.emit(cau_hoi_hien_tai)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        cap.release()
    

    def stop(self):
        self.isRunning = False
        #self.wait()
        print("stop object detection", self.index)
        #self.terminate()
        self.quit()
        #self.wait()
        

class speech_to_text(QThread):
    signal_2 = pyqtSignal(str)
    def __init__(self, index):
        self.index = index
        print("start record", self.index)
        super().__init__()

    def run(self):
        robot_ear = speech_recognition.Recognizer()
        with speech_recognition.Microphone() as mic:
            print("Robot: Tôi đang lắng nghe bạn")
            audio = robot_ear.record(mic, duration=3)
        try:
            you = robot_ear.recognize_google(audio, language="vi")
        except:
            you = ""

        self.signal_2.emit(you) #gửi kết quả thu được về 

    def stop(self):

        print("stop record", self.index)
        self.terminate()
        self.wait()

class show_video_tra_loi_dung(QThread):
    signal_3 = pyqtSignal(np.ndarray)
    def __init__(self, index):
        self.index = index
        print("start post video", self.index)
        super().__init__()

    def run(self):
        cap = cv2.VideoCapture("Chu_cai_va_so/CHINH_XAC_4.mp4")  # 'D:/8.Record video/My Video.mp4'
        while True:
            ret, cv_vid = cap.read()
            if ret:
                self.signal_3.emit(cv_vid)
    def stop(self):
        print("stop post video", self.index)
        self.terminate()
        self.wait()


class Timer_4s(QtCore.QThread):
    signal_4 = pyqtSignal(int)

    def __init__(self, index=0):
        self.index = index
        self.is_running = True
        super().__init__()
    

    def run(self):
        print('Starting thread...', self.index)
        counter = 0
        while True:
            counter += 1
            time.sleep(1)
            if counter == 1:
                number_signal= 111 #chưa đếm
                self.signal_4.emit(number_signal)
                print(counter)
            if counter == 4:
                number_signal = 11 #11 là đếm xong
                self.signal_4.emit(number_signal)
                print(counter)
            if counter == 7:
                number_signal = 123 #chưa đếm
                self.signal_4.emit(number_signal)
                print(counter)
            if counter == 9:
                number_signal = 125 #chưa đếm
                self.signal_4.emit(number_signal)
                print(counter)

    def stop(self):
        self.is_running = False
        print('Stopping thread counter', self.index)
        self.terminate()
        self.wait()
# class mediapipe_capture(QtCore.QThread):
#     signal_5 = pyqtSignal(np.ndarray)
#     signal_5_1 = pyqtSignal(int)
#     def __init__(self, index):
#         self.index = index
#         print("start action recognition thread", self.index)
#         super().__init__()
    
#     def run(self):
#         # 1. New detection variables
#         sequence = []
#         sentence = []
#         predictions = []
#         threshold = 0.8
#         count=[]
#         score_numpy = 0 
#         score_python =0
#         #,cv2.CAP_DSHOW
#         cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
#         cau_hoi_ke_tiep = 6
#         cau_hoi_hien_tai = 6
#         noca = 0 #numbers of correct answer
#         thresh_score = 80 #minimun score để xem đó là 1 nhận diện tốt 
#         with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
#             while cap.isOpened():
#                 t = time.time()
#                 # Read feed
#                 ret, frame = cap.read()

#                 # Make detections
#                 image, results = mediapipe_detection(frame, holistic)
#                 print(results)

#                 # Draw landmarks
#                 draw_styled_landmarks(image, results)

#                 # 2. Prediction logic
#                 keypoints = extract_keypoints(results)
#                 sequence.append(keypoints)
#                 count.append(keypoints)

#                 # Thuật toán đọc kết quả
#                 if len(sequence) == 30:
#                     res = model.predict(np.expand_dims(sequence, axis=0))[0]
#                     print(actions[np.argmax(res)])            
#                     predictions.append(np.argmax(res)) 
#                     score_numpy = res[np.argmax(res)]  
#                     score_python = score_numpy.item()
#                     score_python = score_python *100
#                     score_python = (round(Decimal(score_python),2))            

#                     #3. Viz logic
#                     if np.unique(predictions[-1:])[0]==np.argmax(res): 
#                         if res[np.argmax(res)] > threshold: 

#                             if len(sentence) > 0: 
#                                 if actions[np.argmax(res)] != sentence[-1]:
#                                     sentence.append(actions[np.argmax(res)])
#                             else:
#                                 sentence.append(actions[np.argmax(res)])

#                     if len(sentence) > 1: 
#                             sentence = sentence[-1:]

#                     if (actions[np.argmax(res)] == "aw") & (cau_hoi_hien_tai == 6):
#                         cau_hoi_ke_tiep= 7
#                     if (actions[np.argmax(res)] == "ee") & (cau_hoi_hien_tai == 7):
#                         cau_hoi_ke_tiep= 8
#                     if (actions[np.argmax(res)] == "ow") & (cau_hoi_hien_tai == 8):
#                         cau_hoi_ke_tiep= 9
#                     if (actions[np.argmax(res)] == "sac") & (cau_hoi_hien_tai == 9):
#                         cau_hoi_ke_tiep= 10
#                     if (actions[np.argmax(res)] == "hoi") & (cau_hoi_hien_tai == 10):
#                         cau_hoi_ke_tiep= 11
#                     if (actions[np.argmax(res)] == "nang") & (cau_hoi_hien_tai == 11):
#                         cau_hoi_ke_tiep= 12

#                 elif  len(sequence) > 45 and len(sequence) < 60:
#                     image = draw_class_on_image("STOP", image)
#                     cv2.rectangle(image, (120,200), (int((((len(sequence)-30)/20)*110*4)-150),210), (20,20,200), -1)

#                 elif  len(sequence) == 60:
#                     sequence = []

#                 cv2.rectangle(image, (190,0), (460, 75), (245, 117, 16), -1)
#                 cv2.putText(image, 'Result:', (200,25), 
#                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
#                 cv2.putText(image, ' '.join(sentence), (330,25), 
#                               cv2.FONT_HERSHEY_SIMPLEX, 1, (16,117,245), 2, cv2.LINE_AA)
#                 cv2.putText(image, 'Score:', (200,65), 
#                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
#                 cv2.putText(image, '{}%'.format(score_python), (330,65), 
#                               cv2.FONT_HERSHEY_SIMPLEX, 1, (117,245,16), 2, cv2.LINE_AA)

#                 if ret:
#                     self.signal_5.emit(image)
#                 if cau_hoi_ke_tiep != cau_hoi_hien_tai :
#                     cau_hoi_hien_tai = cau_hoi_ke_tiep
#                     self.signal_5_1.emit(cau_hoi_hien_tai)

#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     cap.release()
                    
#     def stop(self):
#         print("start action recognition thread", self.index)
#         self.terminate()
#         self.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())