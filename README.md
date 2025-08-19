
# 📜 Overview
This project provides a robust solution for Human-Computer Interaction (HCI) by translating hand gestures captured from a standard webcam into precise mouse control actions. It is engineered with a multi-threaded architecture to ensure an "ultra-responsive," lag-free user experience, making it suitable for presentations, accessibility applications, or simply as a futuristic way to interact with your computer.

The system leverages state-of-the-art computer vision libraries to deliver high-fidelity hand tracking and gesture recognition without the need for specialized hardware.

# ✨ Key Features
✅ Real-Time Performance: Low-latency processing for an instantaneous and fluid response to gestures.

✅ Multi-Threaded Architecture: Decouples video processing from mouse control to eliminate input lag and video stutter, a common issue in single-threaded applications.

✅ Intuitive Gestures: Supports a comprehensive set of mouse actions including cursor movement, left/right clicks, double-clicks, and drag-and-drop.

✅ High Configurability: Easily tweakable parameters such as smoothing, pinch sensitivity, and click timings to match user preference.

✅ Cross-Platform: Built with Python and standard libraries, ensuring compatibility with Windows, macOS, and Linux.

# 🛠️ How It Works
The system operates on a sophisticated pipeline that can be broken down into three core stages:

## Vision Pipeline:

OpenCV is used to capture the video feed from the webcam.

Each frame is passed to Google's MediaPipe, which performs the heavy lifting of detecting a hand and mapping its geometry into a skeleton of 21 high-fidelity 3D landmarks.

Gesture Recognition Engine:

The application calculates the Euclidean distance between specific landmarks in real-time to interpret gestures.

For example, a "click" is registered when the distance between the thumb and middle fingertips falls below a predefined threshold. The cursor's position is directly mapped from the index fingertip's landmark.

Asynchronous Control Loop:

This is the key to the application's responsiveness. The main thread (the "producer") handles video capture and gesture detection.

Upon recognizing a gesture, it places an action command (e.g., move, click) into an event queue.

A separate worker thread (the "consumer") continuously monitors this queue and executes the mouse commands via PyAutoGUI. This producer-consumer model ensures that the vision pipeline is never blocked by I/O operations, resulting in a seamless experience.

# 🚀 Getting Started
Follow these instructions to get the project running on your local machine.

Prerequisites
Python 3.8+

A standard webcam

Installation
Clone the repository:

Bash

git clone [https://github.com/your-username/gesture-controlle](https://github.com/BhargabBanerjee/HAND_GESTURE_MOUSE)r.git
cd gesture-controller
Create and activate a virtual environment (recommended):

Bash

python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
Install the required dependencies:
A requirements.txt file should be created with the following content:

opencv-python
mediapipe
pyautogui
Then, run the installer:

Bash

pip install -r requirements.txt
Usage
Execute the main script from your terminal:

Bash

python gesture_controller_v12.py
A window showing your webcam feed will appear. The application is now active. To stop the program, press the Esc key.

# 🔧 Configuration
You can customize the controller's behavior by modifying the constants in the CONFIG section of the script:

# Constant	Description
PINCH_CLOSE_FACTOR	Determines how close fingers must be to register a "pinch" or click. Lower is stricter.
PINCH_OPEN_FACTOR	Determines how far apart fingers must be to register a "release".
DOUBLE_TAP_WINDOW_SEC	The maximum time (in seconds) between two taps to register a double-click.
CURSOR_SMOOTHING	Controls cursor smoothness. A value closer to 0 provides more smoothing but adds latency.
STABLE_GESTURE_FRAMES	Currently not used in v12, but intended for gesture stabilization.
# 🙌 Gesture Reference
Action	Gesture	Implementation
Move Cursor 👆	Point with Index Finger	Maps the index fingertip landmark to screen coordinates.
Left Click 🤏	Tap Thumb & Middle Finger	Detects a rapid pinch and release between thumb and middle finger.
Double Click 🤏🤏	Tap Thumb & Middle Finger Twice	Detects two left-click gestures within the DOUBLE_TAP_WINDOW_SEC.
Right Click 🤙	Tap Thumb & Ring Finger	Detects a pinch between the thumb and ring finger.
Drag & Drop 👍	Pinch & Hold Thumb & Index	A sustained pinch between the thumb and index finger initiates a mouseDown. Releasing the pinch triggers a mouseUp.
⚖️ License
This project is licensed under the MIT License. See the LICENSE file for more details.

# 🙏 Acknowledgments
This project heavily relies on the incredible work done by the teams behind Google's MediaPipe and OpenCV.
