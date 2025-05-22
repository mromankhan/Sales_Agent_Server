from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, firestore, initialize_app
from agentt import agent, Runner



# service_account_info = json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT"))
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred)
db = firestore.client()


# FastAPI init
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
