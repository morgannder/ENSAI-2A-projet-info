import dotenv
from app.api.v1.api import api_router
from fastapi import FastAPI

dotenv.load_dotenv()

app = FastAPI(
    title="Cocktail API", description="API de gestion de cocktails et d'inventaire", version="1.0.0"
)

# Inclusion des routes
app.include_router(api_router, prefix="src/app/api")


@app.get("/")
def read_root():
    return {"message": "Cocktail API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
