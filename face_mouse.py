import cv2
import mediapipe as mp
import pyautogui
import tkinter as tk
from tkinter import messagebox
import hashlib

# ---------------- AUTH MODULE ---------------- #
USER_CREDENTIALS = {
    "Admin": hashlib.sha256("Admin@123".encode()).hexdigest()
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    return USER_CREDENTIALS.get(username) == hash_password(password)

# ---------------- EYE CONTROL MODULE ---------------- #
def is_blinking(upper, lower, frame_h, threshold=5):
    upper_y = int(upper.y * frame_h)
    lower_y = int(lower.y * frame_h)
    return abs(upper_y - lower_y) < threshold

def start_eye_control():
    cam = cv2.VideoCapture(0)
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    screen_w, screen_h = pyautogui.size()

    try:
        while True:
            _, frame = cam.read()
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output = face_mesh.process(rgb_frame)
            landmark_points = output.multi_face_landmarks
            frame_h, frame_w, _ = frame.shape

            if landmark_points:
                landmarks = landmark_points[0].landmark

                # Cursor control using iris landmark
                for id, landmark in enumerate(landmarks[474:478]):
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)
                    cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
                    if id == 1:
                        screen_x = screen_w * landmark.x
                        screen_y = screen_h * landmark.y
                        pyautogui.moveTo(screen_x, screen_y)

                # Get blink landmarks
                left_eye = [landmarks[145], landmarks[159]]
                right_eye = [landmarks[374], landmarks[386]]

                # Draw circles on eye landmarks
                for point in left_eye + right_eye:
                    x = int(point.x * frame_w)
                    y = int(point.y * frame_h)
                    cv2.circle(frame, (x, y), 3, (255, 255, 0), -1)

                # Check if both eyes are blinking
                if is_blinking(left_eye[0], left_eye[1], frame_h) and is_blinking(right_eye[0], right_eye[1], frame_h):
                    pyautogui.click()
                    pyautogui.sleep(1)
                    cv2.putText(frame, "Click", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            cv2.imshow('Eye Controlled Mouse', frame)
            if cv2.waitKey(1) == 27:  # ESC key
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()

# ---------------- LOGIN GUI ---------------- #
def launch_login():
    def login():
        username = username_entry.get()
        password = password_entry.get()
        if verify_login(username, password):
            login_window.destroy()
            start_eye_control()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("300x200")

    tk.Label(login_window, text="Username:").pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    tk.Button(login_window, text="Login", width=15, command=login).pack(pady=20)
    login_window.mainloop()

# ---------------- MAIN ---------------- #
if __name__ == '__main__':
    launch_login()
