import requests
import speech_recognition as sr
import pyttsx3

MODEL = "qwen3:4b"

# Keep only recent conversation messages
conversation = [
    {
        "role": "system",
        "content": """You are Nova, my personal AI assistant.
Always respond in English.
Be helpful and concise.
Keep most answers under 3 sentences unless I ask for details."""
    }
]

# Text-to-speech
engine = pyttsx3.init()
engine.setProperty("rate", 185)

# Speech recognition
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.6
recognizer.energy_threshold = 300


def speak(text):
    print("Nova:", text)
    engine.say(text)
    engine.runAndWait()


def ask_ai(question):

    conversation.append({
        "role": "user",
        "content": question
    })

    # Keep system message + last 8 messages
    messages = [conversation[0]] + conversation[-8:]

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.5,
                "num_predict": 150
            }
        }
    )

    data = response.json()

    answer = data["message"]["content"]

    conversation.append({
        "role": "assistant",
        "content": answer
    })

    return answer


def listen():

    with sr.Microphone() as source:

        print("\n🎤 Listening...")
        audio = recognizer.listen(
            source,
            timeout=5,
            phrase_time_limit=10
        )

    try:
        text = recognizer.recognize_google(audio)

        print("You:", text)

        return text

    except sr.UnknownValueError:
        print("❌ I couldn't understand you.")
        return None

    except sr.RequestError:
        print("❌ Speech recognition service unavailable.")
        return None

    except sr.WaitTimeoutError:
        print("⌛ No speech detected.")
        return None


# Start Nova
speak("Nova is ready.")

while True:

    try:
        user_text = listen()

        if user_text is None:
            continue

        if user_text.lower() in [
            "exit",
            "quit",
            "goodbye",
            "stop",
            "shutdown"
        ]:
            speak("Goodbye!")
            break

        answer = ask_ai(user_text)
        speak(answer)

    except KeyboardInterrupt:
        print("\nNova stopped.")
        break

    except Exception as error:
        print("Error:", error)