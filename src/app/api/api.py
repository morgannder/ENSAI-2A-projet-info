from fastapi import FastAPI
from app.api.endpoints import auth, utilisateurs, inventaire, cocktails
import uvicorn

app = FastAPI(title="User Test API", version="1.0")

app.include_router(auth.router, prefix="/auth")
app.include_router(utilisateurs.router, prefix="/mon_compte")
#app.include_router(inventaire.router, prefix="/inventaire")
#app.include_router(cocktails.router, prefix="/cocktails")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
