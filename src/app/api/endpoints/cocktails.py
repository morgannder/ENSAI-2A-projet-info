from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user, get_current_user_optional
from business_object.utilisateur import Utilisateur
from service.cocktail_service import CocktailService

service_cocktail = CocktailService()
router = APIRouter(tags=["Cocktails"])


class CocktailFilter(BaseModel):
    nom_cocktail: Optional[str] = None
    categorie: Optional[str] = None
    alcool: Optional[str] = None
    verre: Optional[str] = None
    ingredients: Optional[list[str]] = None


@router.post(
    "/cocktails/recherche",
    responses={
        200: {"description": "Liste de cocktails correspondant à vos critères."},
        400: {"description": "Paramètres invalides."},
        500: {"description": "Erreur serveur."},
    },
)
def rechercher_cocktails(
    filtres: CocktailFilter,
    limit: int = 10,
    offset: int = 0,
    utilisateur: Optional[Utilisateur] = Depends(get_current_user_optional),
):
    """
    **Rechercher des cocktails selon vos préférences**

    ## ⚠️ L'abus d'alcool est dangereux pour la santé, à consommer avec modération


    Vous pouvez filtrer par :
    - Nom du cocktail (ex: `"Margarita"`)
    - Type d'alcool (ex: `"Alcoholic"` ou `"Non alcoholic"`)
    - Catégorie (ex: `"Cocktail"`)
    - Verre (ex: `"Highball glass"`)
    - Ingrédients (ex: `["Tequila", "Citron"]`)

    Si vous n'êtes pas connecté, la recherche se fera sans restrictions d'âge.
    Si vous êtes mineur connecté, seuls les cocktails non alcoolisés seront affichés.

    """
    try:
        # Si pas connecté → pas de restriction (None)
        est_majeur = utilisateur.est_majeur if utilisateur else None

        if utilisateur:
            langue = utilisateur.langue
        else:
            langue = "ENG"

        cocktails = service_cocktail.rechercher_par_filtre(
            est_majeur=est_majeur,
            nom_cocktail=filtres.nom_cocktail,
            categ=filtres.categorie,
            alcool=filtres.alcool,
            liste_ingredients=filtres.ingredients,
            verre=filtres.verre,
            langue=langue,
            limit=limit,
            offset=offset,
        )

        if not cocktails:
            raise HTTPException(
                status_code=404,
                detail="Désolé, aucun cocktail n'a pu être trouvé avec vos filtres.",
            )

        return {
            "pagination": {"limit": limit, "offset": offset, "total": len(cocktails)},
            "resultats": [c.__dict__ for c in cocktails],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")


@router.get(
    "/cocktails/complets",
    responses={
        200: {"description": "Liste des cocktails réalisables à 100%."},
        401: {"description": "Vous devez être connecté."},
    },
)
def lister_cocktails_complets(
    limit: int = 10,
    offset: int = 0,
    utilisateur: Utilisateur = Depends(get_current_user),
):
    """
    **Lister les cocktails que vous pouvez réaliser complètement**

    Nécessite d'être connecté pour accéder à votre inventaire.

    ### Paramètres de requête
    - **limit** *(int, optionnel)* : Nombre maximum de cocktails à renvoyer (défaut 10).
    - **offset** *(int, optionnel)* : Décalage pour la pagination.
    """
    if utilisateur:
        langue = utilisateur.langue
    else:
        langue = "ENG"
    try:
        cocktails = service_cocktail.lister_cocktails_complets(
            id_utilisateur=utilisateur.id_utilisateur,
            est_majeur=utilisateur.est_majeur,
            langue=langue,
            limit=limit,
            offset=offset,
        )
        if not cocktails:
            raise HTTPException(
                status_code=404,
                detail="Désolée, mais nous n'avons pas trouvé de cocktail en fonction de votre inventaire. "
                "Nous vous suggérons de rajouter des ingrédients pour plus de choix.",
            )
        return {
            "pagination": {"limit": limit, "offset": offset, "total": len(cocktails)},
            "resultats": [c.__dict__ for c in cocktails],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/cocktails/partiels",
    responses={
        200: {"description": "Liste des cocktails presque réalisables."},
        400: {"description": "Nombre d'ingrédients manquants invalide."},
        401: {"description": "Vous devez être connecté."},
    },
)
def lister_cocktails_partiels(
    nb_manquants: int,
    limit: int = 10,
    offset: int = 0,
    utilisateur: Utilisateur = Depends(get_current_user),
):
    """
    **Lister les cocktails presque réalisables**

    Nécessite d'être connecté pour accéder à votre inventaire.

    ### Paramètres de requête
    - **nb_manquants** *(int, requis)* : Nombre maximal d'ingrédients manquants autorisés (0-5).
    - **limit** *(int, optionnel)* : Nombre maximum de cocktails à renvoyer.
    - **offset** *(int, optionnel)* : Pagination.
    """
    if utilisateur:
        langue = utilisateur.langue
    else:
        langue = "ENG"
    try:
        cocktails = service_cocktail.lister_cocktails_partiels(
            nb_manquants=nb_manquants,
            id_utilisateur=utilisateur.id_utilisateur,
            est_majeur=utilisateur.est_majeur,
            langue=langue,
            limit=limit,
            offset=offset,
        )
        if not cocktails:
            raise HTTPException(
                status_code=404,
                detail="Désolée, aucun cocktail partiellement réalisable n'a été trouvé en fonction de votre inventaire. "
                "Nous vous suggérons de rajouter des ingrédients pour plus de choix.",
            )
        return {
            "pagination": {"limit": limit, "offset": offset, "total": len(cocktails)},
            "resultats": [c.__dict__ for c in cocktails],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/cocktails/aleatoires",
    responses={
        200: {"description": "Sélection aléatoire de cocktails."},
        400: {"description": "Nombre invalide (1-5)."},
    },
)
def cocktails_aleatoires(
    nb: int = 5,
    utilisateur: Optional[Utilisateur] = Depends(get_current_user_optional),
):
    """
    **Obtenir une sélection aléatoire de cocktails**

    ### Paramètres
    - **nb** *(int, optionnel)* : Nombre de cocktails à tirer aléatoirement (max 5, défaut 5).

    ### Réponse
    - Liste aléatoire de cocktails adaptés à l'âge de l'utilisateur si connecté.
    """

    if utilisateur:
        langue = utilisateur.langue
    else:
        langue = "ENG"

    try:
        # Si pas connecté → pas de restriction (None)
        est_majeur = utilisateur.est_majeur if utilisateur else None

        cocktails = service_cocktail.cocktails_aleatoires(
            est_majeur=est_majeur, nb=nb, langue=langue
        )

        return {
            "total": len(cocktails),
            "resultats": [c.__dict__ for c in cocktails],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cocktails/categories")
def lister_categories():
    """
    **Lister les catégories de cocktails**

    Permet d'obtenir la liste complète des catégories présentes dans la base.
    """
    categories = service_cocktail.lister_categories()
    return {"categories": categories}


@router.get("/cocktails/verres")
def lister_verres():
    """
    **Lister les types de verres**

    Permet d'obtenir la liste complète des types de verres présents dans la base.
    """
    verres = service_cocktail.lister_verres()
    return {"verres": verres}
