from fastapi import FastAPI
from routes import logs, goals, feedback, streaks, chat, user

app = FastAPI(
    title="Daily Reflection API",
    version="1.1.0"
)
#app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.include_router(logs.router)
app.include_router(goals.router)
app.include_router(feedback.router)
app.include_router(streaks.router)
app.include_router(chat.router)
app.include_router(user.router)
