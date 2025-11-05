from fastapi import APIRouter, Depends

from app.core.security import oauth2_scheme, verify_token
from service.inventaire_service import InventaireService

router = APIRouter()


@router.get("/{utilisateur_id}")
async def get_inventaire_utilisateur(utilisateur_id: int, token: str = Depends(oauth2_scheme)):
    verify_token(token)
    inventaire_service = InventaireService()
    return inventaire_service.get_inventaire_by_utilisateur(utilisateur_id)
