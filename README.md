🔍 Overview of the Hand Sign Language Teaching System Model
We propose a real-time Vietnamese hand sign language teaching system, using computer vision combined with a deep recurrent neural network. The model consists of three main parts:

🧠 1. Gesture Recognition Module
MediaPipe is used to extract 63 keypoints (x, y, z coordinates) from the user's hand video.

The keypoints in a 30-frame sequence are fed into a Gated Recurrent Unit (GRU) model — a variant of RNN — to learn and classify dynamic hand gestures.

The GRU model structure:

Two GRU layers (256 and 128 units)

Dropout layer to avoid overfitting

Flatten and Dense layers with softmax function to output classification probabilities

Total parameters: 440,884

Performance: Accuracy reached 97.3% on the test set.

🧑‍🏫 3. Interactive Learning Interface (User Interface)
Designed with PyQt5, supporting 3 modes:

Learn: Study letter and number symbols by observing the prosthetic arm.

Test: Practice skills through multiple-choice questions recognizing gestures.

Interpret: Input speech → system translates into sign language.

The interface is intuitive and friendly, especially suitable for children.

📊 Results & Evaluation
Dataset:

12 symbol classes (Vietnamese letters with accents and tone symbols)

Each class has 170 videos

Each video has 30 frames (~1.5 seconds)

Comparison among GRU, LSTM, and RNN shows GRU outperforms in terms of parameter efficiency and accuracy:

Accuracy: 97.3%

Precision, Recall, F1 score, and ROC AUC are also very high

✅ Summary
Combined model components:

MediaPipe → hand skeleton extraction

GRU → dynamic hand sign recognition

3D printed prosthetic arm → sign representation

PyQt5 interface → interactive learning and testing

This is a complete teaching system, suitable for children with hearing or speech impairments, helping to address the shortage of sign language teachers.



![Screenshot from 2025-05-22 08-17-01](https://github.com/user-attachments/assets/bb6cb8a3-c868-4eee-b8e4-267ecdec92a3)

![Screenshot from 2025-05-22 08-14-59](https://github.com/user-attachments/assets/6722a477-a8c5-44dc-99a7-897a2c52defb)
