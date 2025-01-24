import tkinter as tk
import time
import datetime
import math
import pyttsx3
import speech_recognition as sr
import webbrowser
import random
from urllib.parse import quote
import pyautogui
from tkinter import Canvas
import threading
import cv2 
import numpy as np
import os
import pickle
from sklearn.neighbors import KNeighborsClassifier
import sqlite3
from PIL import Image, ImageTk

class VoiceAssistant:
    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Smart Mirror")
        self.root.geometry("800x600+350+50")
        self.root.configure(bg="black")

        self.cap = cv2.VideoCapture(0)
        self.camera_label = tk.Label(self.root)
        self.camera_label.place(x=0, y=0)
        self.stop_camera = True
        self.update_camera()

        self.clock_label = tk.Label(self.root, text="", font=("Helvetica", 12), fg="black",relief="flat")
        self.clock_label.pack(side="left", anchor="n", padx=5, pady=5)
        # self.clock_label.place(x=650, y=0)

        self.date_label = tk.Label(self.root, text="", font=("Helvetica", 12), fg="black",relief="flat")
        self.date_label.pack(side="left", anchor="n", padx=10, pady=5)
        self.date_label.place(y=40)

        self.canvas = Canvas(self.root, width=120, height=120, bg="black", highlightthickness=0)
        self.canvas.pack(side="right", anchor="n",padx=5, pady=5)

        self.center_x = 60
        self.center_y = 60
        self.radius = 60

        self.draw_clock_face()

        self.running = True

        self.voice_button = tk.Button(
            self.root, text="Voice Control", font=("Helvetica", 12), command=self.start_voice_assistant
        )
        self.voice_button.pack()
        self.voice_button.place(relx=0.004, rely=0.996, anchor="sw")

        self.exit_button = tk.Button(
            self.root, text="Exit Voice", font=("Helvetica", 12), command=self.stop_voice_assistant
        )
        self.exit_button.pack()
        self.exit_button.place(relx=0.996, rely=0.996, anchor="se")

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)

        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        self.tasks = []
        self.listening_for_task = False
        self.commands = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
            'farewell': ['bye', 'stop', 'exit', 'quit', 'goodbye'],
            'time': ['time', "what's the time", 'tell me the time'],
            'date': ['date', "what's the date", 'tell me the date'],
            'search': ['search', 'google', 'look up', 'find', 'search for'],
            'task': ['add task', 'add a task', 'new task', 'list tasks', 'show tasks', 'what are my tasks'],
            'screenshot': ['take a screenshot', 'capture screen', 'screenshot'],
            'browser': ['open chrome', 'launch chrome', 'open browser'],
            'thank': ['thank you', 'thanks']
        }

        self.detected_user = None
        self.update_time()

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (800, 600))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
        self.root.after(10, self.update_camera)
      
    def run(self):
        self.greet_user()
        while self.running: 
            query = self.take_command()
            if query:
                self.running = self.process_command(query)
            else:
                time.sleep(1)

    def start_voice_assistant(self):
        self.running = True  
        threading.Thread(target=self.run, daemon=True).start()

    def stop_voice_assistant(self):
        self.running = False  
        self.detected_user = None
        self.speak("Voice assistant is shutting down.")

    def draw_clock_face(self):
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x = self.center_x + self.radius * 0.85 * math.cos(angle)
            y = self.center_y + self.radius * 0.85 * math.sin(angle)
            self.canvas.create_text(x, y, text=str(i if i != 0 else 12), fill="white", font=("Helvetica", 12))

    def draw_analog_clock(self):
        self.canvas.delete("hands")

        now = datetime.datetime.now()
        hour = now.hour % 12 + now.minute / 60.0
        minute = now.minute + now.second / 60.0
        second = now.second

        hour_angle = math.radians(30 * hour - 90)
        minute_angle = math.radians(6 * minute - 90)
        second_angle = math.radians(6 * second - 90)

        hour_x = self.center_x + self.radius * 0.5 * math.cos(hour_angle)
        hour_y = self.center_y + self.radius * 0.5 * math.sin(hour_angle)
        self.canvas.create_line(self.center_x, self.center_y, hour_x, hour_y, fill="white", width=4, tags="hands")

        minute_x = self.center_x + self.radius * 0.7 * math.cos(minute_angle)
        minute_y = self.center_y + self.radius * 0.7 * math.sin(minute_angle)
        self.canvas.create_line(self.center_x, self.center_y, minute_x, minute_y, fill="white", width=2, tags="hands")

        second_x = self.center_x + self.radius * 0.9 * math.cos(second_angle)
        second_y = self.center_y + self.radius * 0.9 * math.sin(second_angle)
        self.canvas.create_line(self.center_x, self.center_y, second_x, second_y, fill="red", width=1, tags="hands")

    def update_time(self):
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%A, %B %d, %Y")
        self.clock_label.config(text=current_time)
        self.date_label.config(text=current_date)
        self.draw_analog_clock()
        self.root.after(1000, self.update_time)

    def speak(self, audio):
        try:
            print(audio)
            self.engine.say(audio)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in speech synthesis: {str(e)}")

    def take_command(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=40, phrase_time_limit=10)
                query = self.recognizer.recognize_google(audio, language="en-in")
                return query.lower()
            except sr.WaitTimeoutError:
                self.speak("Listening timed out. Please try again.")
                return None
            except sr.UnknownValueError:
                self.speak("I couldn't understand that. Could you please repeat?")
                return None
            except sr.RequestError as e:
                self.speak("It seems there's an issue with the speech recognition service. Please check your internet connection.")
                return None
            except Exception as e:
                self.speak("An unexpected error occurred. Please try again.")
                return None

    def greet_user(self):
        self.detect_user_face()
        hour = datetime.datetime.now().hour
        if self.detected_user:
            name = self.detected_user
            if hour < 12:
                self.speak(f"Good Morning, {name}!")
            elif 12 <= hour < 18:
                self.speak(f"Good Afternoon, {name}!")
            else:
                self.speak(f"Good Evening, {name}!")
            self.speak("I'm your voice assistant. How can I help you today?")
        else:
            if hour < 12:
                self.speak("Good Morning!")
            elif 12 <= hour < 18:
                self.speak("Good Afternoon!")
            else:
                self.speak("Good Evening!")
            self.speak("I see a new face. May I know your name?")
            entry = True
            while entry==True:
                self.name = self.take_command()
                if self.name:
                    self.speak(f"Did I hear correctly? Your name is {self.name}, right?")
                    confirmation = self.take_command()
                    conf= True
                    while conf == True:
                        if confirmation != None:
                            if "yes" in confirmation or "correct" in confirmation:
                                self.speak(f"Nice to meet you, {self.name}!")
                                self.speak("Please wait a few seconds to capture your face, and kindly keep your face still in front of the camera.")
                                self.hash_face()
                                self.speak("Your face has been successfully captured. Thank you for your cooperation.")
                                conf = False
                                entry = False
                            elif "no" in confirmation or "not correct" in confirmation or "notcorrect" in confirmation or "not" in confirmation:
                                conf = False 
                                self.speak("Could you please repeat your name?")                        
                            else:
                                self.speak("Could you please repeat the 'Yes' or 'no' for confirmation")
                                confirmation = self.take_command()                   
                        else:
                                self.speak("Could you please repeat the 'Yes' or 'no' for confirmation")
                                confirmation = self.take_command()
                else:
                    self.speak("Could you please repeat your name?")        
         
    def hash_face(self):
        face_data = []
        i = 0
        facecascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        ret = True
        time_limit = 10 
        start_time = time.time()
        while(ret):
            ret, frame = self.cap.read()
            if ret == True:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_coordinates = facecascade.detectMultiScale(gray, 1.2, 3)
                for (a, b, w, h) in face_coordinates:
                    faces = frame[b:b+h, a:a+w, :]
                    resized_faces = cv2.resize(faces, (50, 50))
                    
                    if i % 10 == 0 and len(face_data) < 10:
                        face_data.append(resized_faces)
                i += 1                
                if time.time() - start_time > time_limit or len(face_data) >= 10:
                    break
                if cv2.waitKey(1) == 27:
                    break
            else:
                print('error')
                break
        face_data = np.asarray(face_data)
        face_data = face_data.reshape(10, -1)
        current_directory = os.getcwd()
        base_dir = os.path.join(current_directory, "voice-controlled-smart-mirror-face-data") 
        file_name = "names.pkl"
        file_path = os.path.join(base_dir, file_name)
        os.makedirs(base_dir, exist_ok=True)
        if not os.path.exists(file_path):
            names = [self.name] * 10
            with open(file_path, 'wb') as file:
                pickle.dump(names, file)
        else:
            with open(file_path, 'rb') as file:
                names = pickle.load(file)
            names = names + [self.name] * 10
            with open(file_path, 'wb') as file:
                pickle.dump(names, file)
        current_directory = os.getcwd()
        base_dir = os.path.join(current_directory, "voice-controlled-smart-mirror-face-data")  
        file_name = "faces.pkl"
        file_path = os.path.join(base_dir, file_name)
        os.makedirs(base_dir, exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as w:
                pickle.dump(face_data, w)
        else:
            with open(file_path, 'rb') as w:
                faces = pickle.load(w)
            faces = np.append(faces, face_data, axis=0)
            with open(file_path, 'wb') as w:
                pickle.dump(faces, w)

    def detect_user_face(self):
        facecascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        current_directory = os.getcwd()
        base_dir = os.path.join(current_directory, "voice-controlled-smart-mirror-face-data")
        os.makedirs(base_dir, exist_ok=True)
        faces_file = os.path.join(base_dir, "faces.pkl")
        names_file = os.path.join(base_dir, "names.pkl")
        if os.path.exists(faces_file) and os.path.exists(names_file):
            with open(faces_file, 'rb') as w:
                faces = pickle.load(w)
            with open(names_file, 'rb') as file:
                labels = pickle.load(file)
        else:
            return
        print('Shape of Faces matrix --> ', faces.shape)
        knn = KNeighborsClassifier(n_neighbors=10)
        knn.fit(faces, labels)
        confidence_threshold = 20  
        time_limit = 10  
        start_time = time.time()
        while True:
            ret, frame = self.cap.read()
            if ret == True:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_coordinates = facecascade.detectMultiScale(gray, 1.2, 3)
                for (a, b, w, h) in face_coordinates:
                    fc = frame[b:b + h, a:a + w, :]
                    r = cv2.resize(fc, (50, 50)).flatten().reshape(1, -1)
                    neighbors = knn.kneighbors(r, return_distance=True)
                    distances = neighbors[0][0]
                    max_distance = np.max(distances)
                    confidence = (1 - (np.mean(distances) / max_distance)) * 100
                    text = knn.predict(r)[0]
                    if confidence >= confidence_threshold:
                        self.detected_user = text
                    else:
                        text = "Unknown"  
                if time.time() - start_time > time_limit:
                    break    
                if cv2.waitKey(1) == 27:
                    break
            else:
                print("error")
                break

    def find_command_type(self, query):
        for command_type, phrases in self.commands.items():
            if any(phrase in query for phrase in phrases):
                return command_type
        return None

    def google_search(self, query):
        search_terms = query
        for phrase in self.commands['search']:
            search_terms = search_terms.replace(phrase, "").strip()
        if search_terms:
            self.speak(f"Searching Google for {search_terms}")
            search_url = f"https://www.google.com/search?q={quote(search_terms)}"
            webbrowser.open(search_url)
            return True
        return False

    def manage_tasks(self, query):
        managetask = True
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, task TEXT)''')
        while managetask == True:
            if self.listening_for_task:
                query = self.take_command()
                cursor.execute('INSERT INTO tasks (task) VALUES (?)', (query,))
                conn.commit()
                self.listening_for_task = False
                count = cursor.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
                self.speak(f"Adding {query} to your task list. You now have {count} tasks.")
                managetask = False
            elif any(phrase in query for phrase in ['add task', 'add a task', 'new task']):
                self.listening_for_task = True
                self.speak("Sure, what is the task?")
            elif any(phrase in query for phrase in ['list tasks', 'show tasks', 'what are my tasks']):
                cursor.execute('SELECT task FROM tasks')
                tasks = cursor.fetchall()
                if not tasks:
                    self.speak("You don't have any tasks in your list.")
                    managetask = False
                else:
                    self.speak("Here are your tasks:")
                    for i, task in enumerate(tasks, 1):
                        self.speak(f"Task {i}: {task[0]}")  
                    managetask = False
        conn.close()

    def take_screenshot(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshot_{timestamp}.png"
            pyautogui.screenshot(screenshot_path)
            self.speak(f"I've taken a screenshot and saved it as {screenshot_path}")
        except Exception as e:
            self.speak("Sorry, I couldn't take the screenshot.")
            print(f"Screenshot error: {str(e)}")

    def take_photo(self):
        try:
            ret, frame = self.cap.read()
            if ret:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                photo_path = f"photo_{timestamp}.png"
                cv2.imwrite(photo_path, frame)
                self.speak(f"I've taken a photo and saved it as {photo_path}")
            else:
                self.speak("Sorry, I couldn't capture the photo.")
        except Exception as e:
            self.speak("Sorry, an error occurred while taking the photo.")
            print(f"Photo error: {str(e)}")

    def process_command(self, query):
        try:
            command_type = self.find_command_type(query)
            if command_type == 'greeting':
                responses = ["Hello! How can I help you?", "Hi there! What can I do for you?", "Hey! How may I assist you?"]
                self.speak(random.choice(responses))
            elif command_type == 'farewell':
                self.speak("Goodbye! Have a great day!")
                return False
            elif command_type == 'time':
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                self.speak(f"The current time is {current_time}")
            elif command_type == 'date':
                current_date = datetime.datetime.now().strftime("%B %d, %Y")
                self.speak(f"Today's date is {current_date}")
            elif command_type == 'search':
                if not self.google_search(query):
                    self.speak("What would you like me to search for?")
            elif command_type == 'task':
                self.manage_tasks(query)
            elif command_type == 'screenshot':
                self.take_photo()
            elif command_type == 'photo':
                self.take_screenshot()
            elif command_type == 'browser':
                self.speak("Opening Chrome")
                webbrowser.open("https://www.google.com")
            elif command_type == 'thank':
                responses = ["You're welcome!", "My pleasure!", "Glad I could help!"]
                self.speak(random.choice(responses))
            else:
                self.speak("I heard you say: " + query)
                self.speak("Sorry, I can only help you with tasks like adding and managing tasks, taking screenshots, telling time and date, searching Google, taking photos of your and more.")
            return True

        except Exception as e:
            print(f"Error processing command: {str(e)}")
            self.speak("Sorry, I encountered an error while processing your request.")
            return True

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.root.mainloop()
