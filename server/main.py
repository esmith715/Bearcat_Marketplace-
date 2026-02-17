from fastapi import FastAPI
from routers import listings

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Bearcat Marketplace API is running"}

# Each router should have a router file in routers/ and a service file in services/
# Database connection is established in each service file by importing db/database.py
app.include_router(listings.router, prefix="/listings", tags=["listings"])

# Potential useful routers to develop in the future
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(search.router, prefix="/search", tags=["search"])
# app.include_router(reports.router, prefix="/reports", tags=["reports"])
# app.include_router(admin.router, prefix="/admin", tags=["admin"])
# app.include_router(catalog.router, tags=["catalog"])
# app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
