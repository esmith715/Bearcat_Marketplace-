from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.db.database import create_pool, close_pool
from server.routers import listings, users, reports, search, auth, websockets, notifications, messages, favorites

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_pool()

    yield

    # Shutdown
    await close_pool()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # vite
        "https://hoppscotch.io",
    ],
    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

app.mount("/uploads", StaticFiles(directory=BASE_DIR / "uploads"), name="uploads")
app.mount("/mock", StaticFiles(directory=BASE_DIR / "mock"), name="mock")

@app.get("/")
async def root():
    return {"message": "Bearcat Marketplace API is running"}

app.include_router(listings.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(search.router)
app.include_router(websockets.router)
app.include_router(messages.router)
app.include_router(notifications.router)
app.include_router(favorites.router)

# Potential useful routers to develop in the future
# app.include_router(admin.router, prefix="/admin", tags=["admin"])
# app.include_router(catalog.router, tags=["catalog"])