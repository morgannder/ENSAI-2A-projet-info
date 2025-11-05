from fastapi import APIRouter, Depends

from app.core.security import oauth2_scheme, verify_token
from business_object.utilisateur import Utilisateur
from service.utilisateur_service import UtilisateurService

router = APIRouter()


@router.post("/")
async def creer_utilisateur(utilisateur: Utilisateur):
    utilisateur_service = UtilisateurService()
    return utilisateur_service.creer_compte(utilisateur)


@router.get("/{utilisateur_id}")
async def get_utilisateur(utilisateur_id: int, token: str = Depends(oauth2_scheme)):
    verify_token(token)
    utilisateur_service = UtilisateurService()
    return utilisateur_service.get_utilisateur_by_id(utilisateur_id)
