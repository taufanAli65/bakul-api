from fastapi import FastAPI
from .api.auth import router as auth_router
from .api.users import router as users_router
from .api.products import router as products_router

app = FastAPI()

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(products_router, prefix="/api/v1/products", tags=["products"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Bakul API! Visit /docs for API documentation.",
            "author": "taufan ali",
            "version": "1.0.0"}