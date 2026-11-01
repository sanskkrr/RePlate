from fastapi import FastAPI

from app.database import Base, engine

from app.models.user import User
from app.models.donation import Donation

from app.routers import auth, donations
from app.models.claim import Claim
from app.routers import claims
from app.models.pickup import Pickup
from app.routers import pickups


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="RePlate API",
    description="Surplus Food Rescue and Redistribution Platform",
    version="1.0.0"
)


app.include_router(auth.router)
app.include_router(donations.router)
app.include_router(claims.router)
app.include_router(pickups.router)


@app.get("/")
def home():

    return {
        "message": "Welcome to RePlate API",
        "status": "Running"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }