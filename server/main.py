from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.db.database import create_pool, close_pool
from server.routers import listings, users

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Bearcat Marketplace API is running"}

app.include_router(listings.router)
app.include_router(users.router)

# Potential useful routers to develop in the future
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(search.router, prefix="/search", tags=["search"])
# app.include_router(reports.router, prefix="/reports", tags=["reports"])
# app.include_router(admin.router, prefix="/admin", tags=["admin"])
# app.include_router(catalog.router, tags=["catalog"])
# app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

@app.on_event("startup")
async def startup():
    await create_pool()

@app.on_event("shutdown")
async def shutdown():
    await close_pool()
