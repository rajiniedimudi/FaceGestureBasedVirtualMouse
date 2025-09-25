import cv2
import mediapipe as mp
import pyautogui
import speech_recognition as sr
import random
import util
import threading
import tkinter as tk
from tkinter import messagebox
from pynput.mouse import Button, Controller

# Setup
mouse = Controller()
screen_w, screen_h = pyautogui.size()

# --- Face Mouse Control ---
def face_mouse(frame, frame_h, frame_w, landmarks):
    for id, landmark in enumerate(landmarks[474:478]):
        if id == 1:
            screen_x = screen_w * landmark.x
            screen_y = screen_h * landmark.y
            pyautogui.moveTo(screen_x, screen_y)

    left_eye = [landmarks[145], landmarks[159]]
    right_eye = [landmarks[374], landmarks[386]]

    def is_blinking(upper, lower):
        upper_y = int(upper.y * frame_h)
        lower_y = int(lower.y * frame_h)
        return abs(upper_y - lower_y) < 5

    if is_blinking(*left_eye) and is_blinking(*right_eye):
        pyautogui.click()
        pyautogui.sleep(1)
        cv2.putText(frame, "Click", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

# --- Hand Mouse Control ---
def hand_mouse(frame, frameRGB, hands):
    processed = hands.process(frameRGB)
    landmark_list = []

    if processed.multi_hand_landmarks:
        hand_landmarks = processed.multi_hand_landmarks[0]
        mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

        for lm in hand_landmarks.landmark:
            landmark_list.append((lm.x, lm.y))

        index_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        thumb_index_dist = util.get_distance([landmark_list[4], landmark_list[5]])

        if thumb_index_dist < 50 and util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 90:
            x = int(index_finger_tip.x * screen_w)
            y = int(index_finger_tip.y / 2 * screen_h)
            pyautogui.moveTo(x, y)
        elif util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and util.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) > 90:
            mouse.click(Button.left)
            cv2.putText(frame, "Left Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        elif util.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 90:
            mouse.click(Button.right)
            cv2.putText(frame, "Right Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and util.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50:
            pyautogui.doubleClick()
            cv2.putText(frame, "Double Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        elif thumb_index_dist < 50 and util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50:
            screenshot = pyautogui.screenshot()
            screenshot.save(f"screenshot_{random.randint(100,999)}.png")
            cv2.putText(frame, "Screenshot", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# --- Voice Command Control ---
def voice_commands():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Voice Mode: Listening...")
        try:
            audio = r.listen(source, phrase_time_limit=3)
            cmd = r.recognize_google(audio).lower()
            print("You said:", cmd)
            if "click" in cmd:
                pyautogui.click()
            elif "double click" in cmd:
                pyautogui.doubleClick()
            elif "scroll up" in cmd:
                pyautogui.scroll(500)
            elif "scroll down" in cmd:
                pyautogui.scroll(-500)
        except:
            print("Could not understand voice")

# --- Main Gesture App ---
def main():
    mode = "face"
    cam = cv2.VideoCapture(0)
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    hands = mp.solutions.hands.Hands(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        max_num_hands=1
    )

    voice_thread = threading.Thread(target=voice_commands)
    voice_thread.daemon = True

    print("Press 'f' for Face Mode | 'h' for Hand Mode | 'v' for Voice Mode | 'q' to Quit")

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame_h, frame_w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('f'):
            mode = "face"
        elif key == ord('h'):
            mode = "hand"
        elif key == ord('v'):
            mode = "voice"
        elif key == ord('q'):
            break

        if mode == "face":
            output = face_mesh.process(rgb_frame)
            if output.multi_face_landmarks:
                landmarks = output.multi_face_landmarks[0].landmark
                face_mouse(frame, frame_h, frame_w, landmarks)
            cv2.putText(frame, "Face Mode", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        elif mode == "hand":
            hand_mouse(frame, rgb_frame, hands)
            cv2.putText(frame, "Hand Mode", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        elif mode == "voice":
            if not voice_thread.is_alive():
                voice_thread = threading.Thread(target=voice_commands)
                voice_thread.daemon = True
                voice_thread.start()
            cv2.putText(frame, "Voice Mode", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow("Gesture Controlled Mouse", frame)

    cam.release()
    cv2.destroyAllWindows()

# --- Login GUI ---
def show_login():
    def validate_login():
        username = user_entry.get()
        password = pass_entry.get()
        if username == "Admin" and password == "Admin@123":
            login_win.destroy()
            main()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    login_win = tk.Tk()
    login_win.title("Login")
    login_win.geometry("300x200")
    login_win.resizable(False, False)

    tk.Label(login_win, text="Username").pack(pady=5)
    user_entry = tk.Entry(login_win)
    user_entry.pack(pady=5)

    tk.Label(login_win, text="Password").pack(pady=5)
    pass_entry = tk.Entry(login_win, show="*")
    pass_entry.pack(pady=5)

    tk.Button(login_win, text="Login", command=validate_login).pack(pady=20)
    login_win.mainloop()

# --- Start ---
if __name__ == "__main__":
    show_login()
