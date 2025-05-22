import os
import json
import base64
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, firestore, initialize_app
from agentt import agent, Runner
from dotenv import load_dotenv


load_dotenv()
encoded_key = os.getenv("SERVICE_ACCOUNT_KEY_BASE64")

# Decode and load JSON
decoded_bytes = base64.b64decode(encoded_key)
decoded_json = json.loads(decoded_bytes)

cred = credentials.Certificate(decoded_json)
initialize_app(cred)
db = firestore.client()


# FastAPI init
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000/", "https://sales-agent-eta.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



# chat endpoint
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        uid = data["uid"]
        chat_id = data["chatId"]
        user_message = data["message"]

        messages_ref = (
            db.collection("users")
            .document(uid)
            .collection("chats")
            .document(chat_id)
            .collection("messages")
        )

        # fetch chat history from firebase
        docs = messages_ref.order_by("timestamp").stream()
        history = [
            {"role": doc.to_dict()["role"], "content": doc.to_dict()["content"]}
            for doc in docs
        ]

        # Add latest user message to Firestore and history
        messages_ref.add({
            "role": "user",
            "content": user_message,
            "timestamp": firestore.SERVER_TIMESTAMP,
        })
        history.append({"role": "user", "content": user_message})

        # Generate assistant response
        result = await Runner.run(agent, input=history)
        assistant_message = result.final_output

        # Save assistant reply
        messages_ref.add({
            "role": "assistant",
            "content": assistant_message,
            "timestamp": firestore.SERVER_TIMESTAMP,
        })

        return {"response": assistant_message}

    except Exception as e:
        print("Error in /chat:", e)
        return {"error": str(e)}
# def main():
#     print("Hello from backend!")


# if __name__ == "__main__":
#     main()
