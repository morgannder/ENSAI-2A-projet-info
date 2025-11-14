from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.security import obtenir_utilisateur
from business_object.utilisateur import Utilisateur
from service.cocktail_service import CocktailService
from service.commentaire_service import CommentaireService

router = APIRouter(tags=["Commentaires"])

commentaire_service = CommentaireService()
cocktail_service = CocktailService()


class CommentaireCreate(BaseModel):
    commentaire: str = Field(..., min_length=1, max_length=1000)


Number = Literal["1", "2", "3", "4", "5"]


@router.post("/ajouter_com/{id_cocktail}")
def ajouter_commentaire(
    id_cocktail: int,
    note: Number,
    donnee: CommentaireCreate,
    utilisateur: Utilisateur = Depends(obtenir_utilisateur),
):
    """
    **Ajouter un commentaire sur un cocktail**

    ### Paramètres
    - **id** *int* : id du cocktail
    - **note** *Literal* : Notation sur 5 du cocktail (de 1 à 5)
    - **donnee** *str* : Commentaire de l'utilisateur

    ### Retour
    - Message de confirmation ou d'erreur
    """
    try:
        succes = commentaire_service.ajouter_commentaire(
            id_utilisateur=utilisateur.id_utilisateur,
            id_cocktail=id_cocktail,
            texte=donnee.commentaire,
            note=int(note),
        )
        if succes:
            return {"message": "Commentaire ajouté avec succès"}
        raise HTTPException(status_code=400, detail="Erreur lors de l'ajout du commentaire")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/supprimer_com/{id_cocktail}")
def supprimer_mon_commentaire(
    id_cocktail: int, utilisateur: Utilisateur = Depends(obtenir_utilisateur)
):
    """
    **Supprimer votre commentaire sur un cocktail**

    ### Paramètres
    - **id** *int* : id du cocktail

    ### Réponse
    - Supprime votre commentaire sur ce cocktail
    """
    try:
        # On cherche le commentaire de l'utilisateur pour ce cocktail
        commentaire = commentaire_service.obtenir_commentaire_utilisateur(
            id_utilisateur=utilisateur.id_utilisateur, id_cocktail=id_cocktail
        )

        if not commentaire:
            raise HTTPException(
                status_code=404, detail="Vous n'avez pas de commentaire sur ce cocktail"
            )

        # On utilise l'id du commentaire recuperé au dessus pour pouvoir le supprimé
        # pour l'utilisateur courant (connecté)
        succes = commentaire_service.supprimer_commentaire(
            id_utilisateur=utilisateur.id_utilisateur, id_commentaire=commentaire.id_commentaire
        )

        if succes:
            return {"message": "Votre commentaire a été supprimé avec succès"}
        else:
            raise HTTPException(
                status_code=500, detail="Erreur lors de la suppression du commentaire"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")


@router.get("/liste_com/{id_cocktail}")
def lister_commentaires_cocktail(id_cocktail: int):
    """
    **Lister tous les commentaires d'un cocktail**

    ### Paramètres
    - **id** *int* : id du cocktail

    ### Retour
    - Inclut le nom du cocktail, la note moyenne et tous les commentaires des autres utilisateurs

    """
    try:
        # On recupère les infos du cocktail
        cocktail = cocktail_service.obtenir_cocktail_par_id(id_cocktail)
        if not cocktail:
            raise HTTPException(status_code=404, detail="Cocktail non trouvé")

        # On recupère le commentaire
        commentaires = commentaire_service.lister_commentaires_cocktail(id_cocktail)
        # Eventuel message d'erreur si pas de commentaires pour le cocktail
        if not commentaires:
            raise HTTPException(
                status_code=404,
                detail=f"Aucun commentaire pour l'instant pour ce cocktail : {cocktail.nom_cocktail}",
            )
        note_moyenne = commentaire_service.calculer_note_moyenne(id_cocktail)

        # Formatage de la réponse côté utilisateur
        response = {
            "cocktail": {
                "id_cocktail": cocktail.id_cocktail,
                "nom_cocktail": cocktail.nom_cocktail,
                "note_moyenne": round(note_moyenne, 1),  # Arrondir à 1 décimale
                "nombre_commentaires": len(commentaires),
            },
            "commentaires": [],
        }

        for commentaire in commentaires:
            commentaire_data = {
                "pseudo_utilisateur": commentaire.pseudo_utilisateur,
                "date_commentaire": commentaire.date_creation.strftime("%d/%m/%Y"),
                "note": commentaire.note,
                "texte": commentaire.texte,
            }

            response["commentaires"].append(commentaire_data)

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")


@router.get("/mes_commentaires")
def lister_mes_commentaires(utilisateur: Utilisateur = Depends(obtenir_utilisateur)):
    """
    **Lister tous mes commentaires**

      ### Paramètres
    - Aucun

    ### Retour
    - Retourne tous les commentaires que l'utilisateur connecté a posté sur différents cocktails
    - Inclut les informations des cocktails associés
    """
    try:
        # Récupérer tous les commentaires de l'utilisateur connecté
        mes_commentaires = commentaire_service.obtenir_commentaires_par_utilisateur(
            id_utilisateur=utilisateur.id_utilisateur
        )

        if not mes_commentaires:
            raise HTTPException(
                status_code=404, detail="Vous n'avez posté aucun commentaire pour le moment"
            )

        # Formatage de la réponse
        response = {
            "utilisateur": {"nombre_total_commentaires": len(mes_commentaires)},
            "mes_commentaires": [],
        }

        for commentaire in mes_commentaires:
            # ON recupère les infos du cocktail associé
            cocktail = cocktail_service.obtenir_cocktail_par_id(commentaire.id_cocktail)

            commentaire_data = {
                "cocktail": {
                    "id_cocktail": cocktail.id_cocktail if cocktail else None,
                    "nom_cocktail": cocktail.nom_cocktail if cocktail else "Cocktail inconnu",
                },
                "date_commentaire": commentaire.date_creation.strftime("%d/%m/%Y"),
                "note": commentaire.note,
                "texte": commentaire.texte,
            }

            response["mes_commentaires"].append(commentaire_data)

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")
