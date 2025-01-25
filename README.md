# Smart Mirror Voice Assistant
This project is a voice-controlled smart mirror application built using Python and the Tkinter library for the GUI. It integrates various functionalities such as time and date display, voice commands for searching the web, task management, and face recognition.

### Features
1.	Live Camera Feed:
    *	Captures live video feed using OpenCV.
    *	Displays the camera output on the GUI.
2.	Clock and Date Display:
    *	Digital time and date are shown on the mirror.
    *	Analog clock implemented using Tkinter Canvas.
3.	Voice Assistant:
    *	Uses pyttsx3 for text-to-speech.
    *	Uses speech_recognition for voice input.
    *	Handles commands such as:
      -	Greeting and farewell
      -	Fetching the current time and date
      -	Google search
      -	Task management
      -	Taking screenshots
      -	Taking photos
4.	Face Recognition:
    *	Uses OpenCV for face detection.
    *	Recognizes users and greets them accordingly.
    *	Stores face data for future recognition.
5.	Task Management:
    *	Saves tasks in an SQLite database.
    *	Allows users to add and list tasks using voice commands.
6.	Web Browser Control:
    *	Opens the Chrome browser for web searches.
7.	Screenshot and Photo Capture:
    *	Captures screenshots of the screen.
    *	Takes and saves photos from the live camera feed.

# Installation
Install the required packages:
  ```
  pip install -r requirements.txt
  ```
# Usage
  *	Click on Voice Control to activate the voice assistant.
  *	Say commands such as:
    *	"What's the time?"
    *	"Take a screenshot"
    *	"Google search"
    *	"Add task"
    *	"Show tasks"
  *	Click on Exit Voice to shut down the assistant.

# Code Explanation
*	Tkinter GUI setup:
	-	Configuring the mirror interface with time, date, and camera feed.
*	Voice assistant functionality:
	-	Listens for user commands and processes them using speech_recognition.
	-	Provides spoken responses via pyttsx3.
*	Face recognition module:
	-	Captures user images and detects faces using OpenCV.
	-	Greets recognized users.
*	Task management system:
	-	Stores tasks in an SQLite database.
	-	Retrieves and displays tasks based on voice commands.
*	Screenshot and photo capture:
	-	Saves the current screen or captures images from the camera.

# Future Improvements
*	Implement weather updates display.
*	Add voice-based mirror settings configuration.
*	Improve face recognition accuracy.

# Acknowledgments
*	OpenCV for image processing
*	Tkinter for GUI development
*	Pyttsx3 for text-to-speech conversion
