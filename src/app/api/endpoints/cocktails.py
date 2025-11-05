from fastapi import APIRouter, Depends

from app.core.security import oauth2_scheme, verify_token
from service.cocktail_service import CocktailService

router = APIRouter()


@router.get("/")
async def get_cocktails(token: str = Depends(oauth2_scheme)):
    verify_token(token)
    cocktail_service = CocktailService()
    return cocktail_service.get_cocktails()


@router.get("/{cocktail_id}")
async def get_cocktail(cocktail_id: int, token: str = Depends(oauth2_scheme)):
    verify_token(token)
    cocktail_service = CocktailService()
    return cocktail_service.get_cocktail_by_id(cocktail_id)
