from typing import Literal

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import obtenir_utilisateur
from business_object.utilisateur import Utilisateur
from service.inventaire_service import InventaireService
from service.utilisateur_service import UtilisateurService

router = APIRouter(tags=["Inventaire"])
service_inventaire = InventaireService()
service_utilisateur = UtilisateurService()


Number = Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]


@router.get("/vue")
def consulte_inventaire(utilisateur: Utilisateur = Depends(obtenir_utilisateur)):
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
def suggestion_ingredients(nombre: Number):
    """
    **Retourne jusqu'à n ingrédients au hasard pour aider l'utilisateur.**
    ### Paramètres
    - **n** *Literal* : Nombre d'ingrédients à suggérer

    ### Retour
    Liste de nom d'ingrédient
    """
    suggestions = service_inventaire.suggerer_ingredients(int(nombre))
    return [ing.nom_ingredient for ing in suggestions]


@router.put("/ajouter")
def ajoute_ingredient(
    demande_ingredient: str, utilisateur: Utilisateur = Depends(obtenir_utilisateur)
):
    """
    **Ajoute un ingrédient à l'inventaire de l'utilisateur**

    ### Paramètres
    - **demande_ingredient** *str* : ingrédient à ajouter à l'inventaire

    ### Retour
    Message de confirmation ou d'erreur
    """
    try:
        requete = service_inventaire.recherche_ingredient(demande_ingredient)
        if service_inventaire.ajouter(utilisateur.id_utilisateur, requete):
            return {"Information": "L'ingrédient a été ajouté à l'inventaire !"}

    except Exception as e:
        print("DEBUG /inventaire/vue: exception", e)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de l'ajout de l'inventaire",
        )


@router.delete("/supprimer_ingredient")
def supprime_ingredient(
    demande_ingredient: str, utilisateur: Utilisateur = Depends(obtenir_utilisateur)
):
    """
    **Supprime un ingrédient à l'inventaire de l'utilisateur**

    ### Paramètres
    - **demande_ingredient** *str* : ingrédient à supprimer de l'inventaire

    ### Retour
    Message de confirmation ou d'erreur
    """
    try:
        requete = service_inventaire.recherche_ingredient(demande_ingredient)
        if service_inventaire.supprimer(
            utilisateur.id_utilisateur, requete.id_ingredient):
            return {"Information": "L'ingrédient a été supprimé de l'inventaire !"}
        elif not service_inventaire.supprimer(
            utilisateur.id_utilisateur, requete.id_ingredient):
            return {"Information": "Vous ne possédez pas cet ingrédient dans votre inventaire !"}

    except Exception as e:
        print("DEBUG /inventaire/vue: exception", e)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la suppression de l'inventaire",
        )


@router.delete("/supprimer_tout")
def supprimer_mon_inventaire(
    reponse: str, utilisateur: Utilisateur = Depends(obtenir_utilisateur)
):
    """
    **Supprime l'inventaire de l'utilisateur**

    ### Paramètres
    - **confirmation** *str* saisir 'CONFIRMER' pour valider la demande de suppression
            de l'inventaire

    ### Retour
    Message de confirmation ou d'erreur
    """
    try:
        if reponse == "CONFIRMER":
            # Appeler le service pour supprimer le compte
            suppression_reussie = service_utilisateur.supprimer_inventaire(utilisateur)

            if not suppression_reussie:
                raise HTTPException(
                    status_code=500,
                    detail="Erreur lors de la suppression de l'inventaire",
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
