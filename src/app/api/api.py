from fastapi import APIRouter

from app.api.endpoints import auth, cocktails, commentaire, inventaire, utilisateurs

# Création du routeur principal
api_router = APIRouter()

# Inclusion des routeurs
api_router.include_router(auth.router, prefix="/auth", tags=["Authentification"])
api_router.include_router(
    utilisateurs.router, prefix="/mon_compte", tags=["Utilisateur"]
)
api_router.include_router(inventaire.router, prefix="/inventaire", tags=["Inventaire"])
api_router.include_router(cocktails.router, prefix="/cocktails", tags=["Cocktails"])
api_router.include_router(
    commentaire.router, prefix="/commentaires", tags=["Commentaires"]
)

# Export explicite
__all__ = ["api_router"]
