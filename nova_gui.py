import customtkinter as ctk
import requests
import threading
import speech_recognition as sr
import pyttsx3

MODEL = "qwen3:4b"

conversation = [
    {
        "role": "system",
        "content": "You are Nova, a fast personal AI assistant. Reply in English and be concise."
    }
]

# Voice
engine = pyttsx3.init()
engine.setProperty("rate", 185)

recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.6


def speak(text):
    engine.say(text)
    engine.runAndWait()


# AI
# AI
def ask_ai(question):
    conversation.append({
        "role": "user",
        "content": question
    })

    messages = [conversation[0]] + conversation[-4:]

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.4,
                "num_predict": 120
            }
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    print("OLLAMA RESPONSE:", data)

    answer = data["message"]["content"]

    conversation.append({
        "role": "assistant",
        "content": answer
    })

    return answer

# Interface
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Nova AI")
app.geometry("950x650")
app.minsize(750, 550)


# Sidebar
sidebar = ctk.CTkFrame(app, width=210, corner_radius=0)
sidebar.pack(side="left", fill="y")

title = ctk.CTkLabel(
    sidebar,
    text="✦ NOVA",
    font=("Segoe UI", 28, "bold")
)
title.pack(pady=(35, 10))

subtitle = ctk.CTkLabel(
    sidebar,
    text="Personal AI Assistant",
    font=("Segoe UI", 13)
)
subtitle.pack(pady=(0, 40))

new_chat = ctk.CTkButton(
    sidebar,
    text="+  New Chat",
    height=40,
    corner_radius=10
)
new_chat.pack(padx=20, fill="x")

status = ctk.CTkLabel(
    sidebar,
    text="●  Online",
    font=("Segoe UI", 13)
)
status.pack(side="bottom", pady=30)


# Main area
main = ctk.CTkFrame(app, corner_radius=0)
main.pack(side="right", fill="both", expand=True)


# Header
header = ctk.CTkFrame(
    main,
    height=70,
    fg_color="transparent"
)
header.pack(fill="x", padx=25, pady=(15, 0))

header_title = ctk.CTkLabel(
    header,
    text="Nova",
    font=("Segoe UI", 22, "bold")
)
header_title.pack(side="left")

header_status = ctk.CTkLabel(
    header,
    text="Ready",
    font=("Segoe UI", 13)
)
header_status.pack(side="right")


# Chat
chat = ctk.CTkTextbox(
    main,
    corner_radius=12,
    font=("Segoe UI", 15),
    wrap="word"
)
chat.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=10
)

chat.configure(state="disabled")


def add_message(sender, message):
    chat.configure(state="normal")

    chat.insert(
        "end",
        f"\n{sender}\n"
    )

    chat.insert(
        "end",
        f"{message}\n\n"
    )

    chat.configure(state="disabled")
    chat.see("end")


# Process message
def process_message(message):

    add_message("You", message)
    header_status.configure(text="Thinking...")

    def get_response():

        try:
            answer = ask_ai(message)

            app.after(
                0,
                lambda: add_message("✦ Nova", answer)
            )

            app.after(
                0,
                lambda: header_status.configure(text="Ready")
            )

            threading.Thread(
                target=speak,
                args=(answer,),
                daemon=True
            ).start()

        except Exception as error:

            app.after(
                0,
                lambda: add_message(
                    "Nova",
                    f"Error: {error}"
                )
            )

            app.after(
                0,
                lambda: header_status.configure(text="Error")
            )

    threading.Thread(
        target=get_response,
        daemon=True
    ).start()


# Send button
def send_message():

    message = entry.get().strip()

    if not message:
        return

    entry.delete(0, "end")

    process_message(message)


# Input
input_frame = ctk.CTkFrame(
    main,
    fg_color="transparent"
)
input_frame.pack(
    fill="x",
    padx=25,
    pady=(5, 20)
)

entry = ctk.CTkEntry(
    input_frame,
    placeholder_text="Ask Nova anything...",
    height=50,
    corner_radius=15,
    font=("Segoe UI", 14)
)
entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(0, 10)
)


# Send button
send_button = ctk.CTkButton(
    input_frame,
    text="➤",
    width=55,
    height=50,
    corner_radius=15,
    font=("Segoe UI", 20),
    command=send_message
)
send_button.pack(side="right")


# Microphone
def voice_input():

    header_status.configure(text="Listening...")

    def listen():

        try:

            with sr.Microphone() as source:

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=10
                )

            text = recognizer.recognize_google(audio)

            app.after(
                0,
                lambda: process_message(text)
            )

        except Exception as error:

            app.after(
                0,
                lambda: header_status.configure(text="Ready")
            )

    threading.Thread(
        target=listen,
        daemon=True
    ).start()


mic_button = ctk.CTkButton(
    input_frame,
    text="🎤",
    width=55,
    height=50,
    corner_radius=15,
    command=voice_input
)
mic_button.pack(
    side="right",
    padx=(0, 10)
)


# Enter key
entry.bind(
    "<Return>",
    lambda event: send_message()
)


# Welcome message
add_message(
    "✦ Nova",
    "Hello! I'm Nova. Welcome master. How can I assist you today?"
)


app.mainloop()