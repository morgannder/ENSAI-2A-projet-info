from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user
from business_object.utilisateur import Utilisateur
from service.inventaire_service import InventaireService
from service.utilisateur_service import UtilisateurService

router = APIRouter(tags=["Inventaire"])
service_inventaire = InventaireService()
service_utilisateur = UtilisateurService()


class Reponse(BaseModel):
    confirmation: str


@router.get("/vue")
def consulte_inventaire(utilisateur: Utilisateur = Depends(get_current_user)):
    """**Montre l'inventaire de l'utilisateur**"""
    try:
        return service_inventaire.lister(utilisateur.id_utilisateur)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("DEBUG /inventaire/vue: exception", e)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la visualisation de l'inventaire",
        )


@router.get(
    "/suggestion",
    responses={
        200: {"description": "Sélection aléatoire de cocktails."},
        400: {"description": "Paramètre invalide."},
    },
)
def suggestion_ingredients(n: int = 5):
    """
    **Retourne jusqu'à n ingrédients au hasard pour aider l'utilisateur.**

    Limité entre 1 et 10 ingrédients.
    """
    suggestions = service_inventaire.suggerer_ingredients(n)
    return [ing.nom_ingredient for ing in suggestions]


@router.put("/ajouter")
def ajoute_ingredient(
    demande_ingredient: str, utilisateur: Utilisateur = Depends(get_current_user)
):
    """**Ajoute un ingrédient à l'inventaire de l'utilisateur**

    Vous pouvez consulter les ingrédients disponibles via la méthode de suggestion d'ingrédients
    """
    try:
        requete = service_inventaire.recherche_ingredient(demande_ingredient)
        return service_inventaire.ajouter(utilisateur.id_utilisateur, requete)

    except Exception as e:
        print("DEBUG /inventaire/vue: exception", e)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de l'ajout de l'inventaire",
        )


@router.delete("/supprimer_ingredient")
def supprime_ingredient(
    demande_ingredient: str, utilisateur: Utilisateur = Depends(get_current_user)
):
    """**Supprime un ingrédient à l'inventaire de l'utilisateur**"""
    try:
        requete = service_inventaire.recherche_ingredient(demande_ingredient)
        return service_inventaire.supprimer(utilisateur.id_utilisateur, requete.id_ingredient)

    except Exception as e:
        print("DEBUG /inventaire/vue: exception", e)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la suppression de l'inventaire",
        )


@router.delete("/supprimer_tout")
def supprimer_mon_inventaire(
    reponse: Reponse, utilisateur: Utilisateur = Depends(get_current_user)
):
    """
    Supprime l'inventaire de l'utilisateur

    Veuillez saisir 'CONFIRMER' pour valider la demande
    """
    try:
        if reponse.confirmation == "CONFIRMER":
            # Appeler le service pour supprimer le compte
            suppression_reussie = service_utilisateur.supprimer_inventaire(utilisateur)

            if not suppression_reussie:
                raise HTTPException(
                    status_code=500, detail="Erreur lors de la suppression de l'inventaire"
                )

            return {
                "message": "Inventaire supprimé avec succès.",
                "supprime": True,
            }
        else:
            raise HTTPException(
                status_code=409,
                detail="Erreur de conflit, vous devez taper CONFIRMER dans le champ de confirmation pour valider votre requête",
            )
    except HTTPException:
        raise
    except Exception as e:
        print("DEBUG /register: exception", e)
        raise HTTPException(
            status_code=500, detail="Erreur interne lors de la suppression du compte"
        )
