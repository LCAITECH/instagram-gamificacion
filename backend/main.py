from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Gamified Community Engine")

# CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all. Limit this in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .routers import webhooks, users
app.include_router(webhooks.router)
app.include_router(users.router)

# Mount Frontend (Must be last to not override API routes)
import os
frontend_path = os.path.join(os.getcwd(), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.get("/api/health")
def read_root():
    return {"message": "Game Engine is Running 🚀"}

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
