import dotenv
from fastapi import FastAPI

from app.api.api import api_router

dotenv.load_dotenv()

app = FastAPI(
    title="Cocktail API", description="API de gestion de cocktails et d'inventaire", version="1.0.0"
)

# Inclusion des routes
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
