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
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap,QImage
from PyQt5.QtWidgets import QApplication, QMainWindow,QFileDialog, QMessageBox, QLabel
from Giao_dien_test import Ui_MainWindow
from PyQt5 import QtWidgets
from Sub_page_5_nckh import Ui_Form
import speech_recognition
from decimal import Decimal

from Chuyen_co_dau_thanh_khong_dau import ma_hoa_telex

