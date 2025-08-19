#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gesture Controller v12.0 — Ultra Responsive Edition
- Multi-threaded: camera loop + gesture logic + mouse control
- Event coalescing for smooth cursor moves
- No frame lag, no blocked clicks
"""

import cv2
import mediapipe as mp
import pyautogui
import time
import threading
import queue
import math

# ========== CONFIG ==========
PINCH_CLOSE_FACTOR = 0.18
PINCH_OPEN_FACTOR = 0.35
DOUBLE_TAP_WINDOW_SEC = 0.35
CLICK_COOLDOWN_SEC = 0.4
CURSOR_SMOOTHING = 0.25
STABLE_GESTURE_FRAMES = 4

# ========== INIT ==========
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7,
                       min_tracking_confidence=0.7,
                       max_num_hands=1)
mp_draw = mp.solutions.drawing_utils
screen_w, screen_h = pyautogui.size()

# Shared state
event_q = queue.Queue()
cursor_lock = threading.Lock()
latest_cursor = None

# ========== HELPERS ==========
def dist(lm, a, b):
    return math.hypot(lm[a].x - lm[b].x, lm[a].y - lm[b].y)

def action_allowed(last_time, cooldown):
    return (time.perf_counter() - last_time) > cooldown

# ========== MOUSE THREAD ==========
def mouse_worker():
    global latest_cursor
    last_left_click = 0
    dragging = False
    while True:
        try:
            # process all queued events quickly
            while not event_q.empty():
                action, val = event_q.get_nowait()
                if action == "move":
                    with cursor_lock:
                        latest_cursor = val
                elif action == "click":
                    pyautogui.click()
                elif action == "double_click":
                    pyautogui.doubleClick()
                elif action == "right_click":
                    pyautogui.rightClick()
                elif action == "mouse_down":
                    if not dragging:
                        pyautogui.mouseDown()
                        dragging = True
                elif action == "mouse_up":
                    if dragging:
                        pyautogui.mouseUp()
                        dragging = False
        except queue.Empty:
            pass

        # move cursor to latest position (coalesced)
        with cursor_lock:
            if latest_cursor is not None:
                x, y = latest_cursor
                pyautogui.moveTo(x, y, duration=0)
                latest_cursor = None

        time.sleep(0.005)  # 200 Hz update loop

threading.Thread(target=mouse_worker, daemon=True).start()

# ========== MAIN LOOP ==========
cap = cv2.VideoCapture(0)
gesture_history = []
stable_gesture = None
stable_count = 0

last_left_tap_time = 0
left_tap_state = "IDLE"
right_tap_state = "IDLE"
dragging = False

prev_x, prev_y = pyautogui.position()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    status = "None"

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        lm = hand.landmark
        h, w, _ = frame.shape
        hand_size = dist(lm, 0, 9)

        # ==== Cursor Control ====
        idx_x, idx_y = int(lm[8].x * w), int(lm[8].y * h)
        scr_x = int((lm[8].x) * screen_w)
        scr_y = int((lm[8].y) * screen_h)

        # smoothing
        scr_x = int(prev_x + (scr_x - prev_x) * CURSOR_SMOOTHING)
        scr_y = int(prev_y + (scr_y - prev_y) * CURSOR_SMOOTHING)
        prev_x, prev_y = scr_x, scr_y
        event_q.put(("move", (scr_x, scr_y)))

        # ==== Gesture Detection ====
        close_t = PINCH_CLOSE_FACTOR * hand_size
        open_t = PINCH_OPEN_FACTOR * hand_size
        now = time.perf_counter()

        # Selection (thumb-index hold)
        sel_d = dist(lm, 4, 8)
        if sel_d < close_t and not dragging:
            event_q.put(("mouse_down", None))
            dragging = True
            status = "Selecting"
        elif sel_d > open_t and dragging:
            event_q.put(("mouse_up", None))
            dragging = False
            status = "Selection End"

        # Clicks (only if not dragging)
        if not dragging:
            # Left click (thumb-middle tap)
            left_d = dist(lm, 4, 12)
            if left_d < close_t and left_tap_state == "IDLE":
                left_tap_state = "TAPPED"
                if (now - last_left_tap_time) < DOUBLE_TAP_WINDOW_SEC:
                    event_q.put(("double_click", None))
                    status = "Double Click"
                    last_left_tap_time = 0
                else:
                    event_q.put(("click", None))
                    status = "Click"
                    last_left_tap_time = now
            elif left_d > open_t:
                left_tap_state = "IDLE"

            # Right click (thumb-ring tap)
            right_d = dist(lm, 4, 16)
            if right_d < close_t and right_tap_state == "IDLE":
                right_tap_state = "TAPPED"
                event_q.put(("right_click", None))
                status = "Right Click"
            elif right_d > open_t:
                right_tap_state = "IDLE"

        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    cv2.putText(frame, f"Gesture: {status}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Gesture Controller v12.0", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
