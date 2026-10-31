import requests

MODEL = "qwen3:4b"

conversation = [
    {
        "role": "system",
        "content": """You are my personal AI assistant.
Your name is Nova.
Always respond in English unless I ask for another language.
Be helpful, friendly, and concise.
Remember the conversation during this session."""
    }
]


def ask_ai(message):
    conversation.append({
        "role": "user",
        "content": message
    })

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": MODEL,
            "messages": conversation,
            "stream": False
        }
    )

    data = response.json()

    answer = data["message"]["content"]

    conversation.append({
        "role": "assistant",
        "content": answer
    })

    return answer


print("================================")
print("🤖 NOVA - Your AI Assistant")
print("================================")
print("Type 'exit' to stop.\n")


while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Nova: Goodbye!")
        break

    try:
        answer = ask_ai(user_input)
        print("\nNova:", answer)
        print()

    except Exception as error:
        print("Error:", error)