import tkinter as tk
from tkinter import messagebox
import hashlib
import speech_recognition as sr
import pyautogui

# ---------------- AUTH MODULE ---------------- #
USER_CREDENTIALS = {
    "Admin": hashlib.sha256("Admin@123".encode()).hexdigest()
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    return USER_CREDENTIALS.get(username) == hash_password(password)

# ---------------- VOICE CONTROL MODULE ---------------- #
r = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            cmd = r.recognize_google(audio)
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
            print("Sorry, couldn't understand")

def start_voice_control():
    while True:
        listen()

# ---------------- LOGIN GUI ---------------- #
def launch_login():
    def login():
        username = username_entry.get()
        password = password_entry.get()
        if verify_login(username, password):
            login_window.destroy()
            start_voice_control()
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
