from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import users, tasks

# ---=== Initiate the API core ===---
app = FastAPI()

# ---=== Add middleware allows to interact with the javascript ===---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---=== Setup SQLAlchemy database ===---
Base.metadata.create_all(bind=engine)

# ---=== Setup our API command routers ===---
app.include_router(users.router)
app.include_router(tasks.router)