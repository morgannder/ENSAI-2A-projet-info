# app/api/endpoints/utilisateurs.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.security import obtenir_utilisateur
from business_object.utilisateur import Utilisateur
from service.utilisateur_service import UtilisateurService

router = APIRouter(tags=["Utilisateur"])
service_utilisateur = UtilisateurService()


class UserUpdate(BaseModel):
    nouveau_pseudo: Optional[str] = Field(
        None,
        description=(
            "Nouveau pseudo souhaité pour votre compte. "
            "Doit contenir au moins 3 caractères. "
            "Le pseudo doit être unique."
        ),
    )

    nouveau_mdp: Optional[str] = Field(
        None,
        description=(
            "Nouveau mot de passe. Il doit respecter les règles de sécurité décrites lors de "
            "l'inscription"
        ),
    )

    langue: Optional[str] = Field(
        None, description=("Nouvelle langue d’affichage préférée pour les recettes")
    )


class Reponse(BaseModel):
    confirmation: str


LANGUES_VALIDES = {"string", "FRA", "ESP", "ITA", "ENG", "GER"}


@router.get("/informations", tags=["Utilisateur"])
def mes_informations(utilisateur: Utilisateur = Depends(obtenir_utilisateur)):
    """
    **Visualiser les informations de votre compte**

    Comprends les champs suivants :

    - **pseudo** → votre pseudo
    - **age** → votre âge
    - **langue**  → langue pour les recettes
    - **date_creation** → date de création de votre compte
    """
    print("DEBUG /me appelé pour l'utilisateur:", utilisateur)

    return {
        "pseudo": utilisateur.pseudo,
        "age": utilisateur.age,
        "langue": utilisateur.langue,
        "date_création": utilisateur.date_creation.strftime("%d/%m/%Y"),
        "cocktails_recherchés": utilisateur.cocktails_recherches,
    }


@router.put("/mettre_a_jour", tags=["Utilisateur"])
def modifie_compte(donnee: UserUpdate, utilisateur: Utilisateur = Depends(obtenir_utilisateur)):
    """
    **Modifie certaines informations du compte**

    ### Paramètre
    - **donnee** *dict* saisir les informations pour valider la modification du compte,
            supprimer la clé pour ne pas la modifier

    ### Réponse
    Message de confirmation ou d'erreur
        affiche les champs modifiés avec succès ainsi que les erreurs potentielles sur les champs
        entrés
    """
    print("DEBUG /me/update: données reçues:", donnee)
    print("DEBUG /me/update: utilisateur avant update:", utilisateur)

    # Vérification qu'il y a au moins un champ à modifier
    if not any([donnee.nouveau_pseudo, donnee.nouveau_mdp, donnee.langue]):
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")

    changements = []
    erreurs = []

    try:
        # Verification du nouveau pseudo
        if donnee.nouveau_pseudo:
            if donnee.nouveau_pseudo == utilisateur.pseudo or len(donnee.nouveau_pseudo) < 3:
                erreurs.append("Le nouveau pseudo doit être différent de l'ancien et contenir "
                               "au moins 3 charactères")
            else:
                succes = service_utilisateur.changer_pseudo(utilisateur, donnee.nouveau_pseudo)
                if succes:
                    changements.append("pseudo")
                else:
                    erreurs.append("Pseudo déjà utilisé")

        # Verification du nouveau mdp
        if donnee.nouveau_mdp:
            resultat = service_utilisateur.changer_mdp(utilisateur, donnee.nouveau_mdp)
            if resultat == "identique":
                erreurs.append("Le nouveau mot de passe est identique à l'ancien")
            elif resultat == "erreur":
                erreurs.append("Erreur lors du changement de mot de passe")
            elif resultat == "erreurs_mdp":
                erreurs.append("Mot de passe non conforme aux règles de sécurités")
            else:
                changements.append("mot de passe")

        # Verification de la nouvelle langue
        if donnee.langue:
            if donnee.langue not in LANGUES_VALIDES:
                erreurs.append(f"Langue '{donnee.langue}' non valide. Langues acceptées : {', '.join(sorted(LANGUES_VALIDES))}")
            else:
                succes = service_utilisateur.choisir_langue(utilisateur, donnee.langue)
                if succes:
                    changements.append("langue")
                else:
                    erreurs.append("Erreur lors de la modification de la langue")

        # Gestion du resultat final
        if erreurs and not changements:
            # Aucune modif reussie (que des erreurs)
            raise HTTPException(
                status_code=400,
                detail={"erreurs": erreurs, "message": "Aucune modification n'a pu être effectuée"}
            )
        elif erreurs and changements:
            # Modifs partielles avec certaines erreurs
            return {
                "message": "Modification partiellement réussie",
                "changements_effectues": changements,
                "erreurs": erreurs,
                "utilisateur": utilisateur.pseudo,
            }
        else:
            # Toutes les modifs ont réussi
            return {
                "message": f"Modification réussie : {', '.join(changements)}",
                "utilisateur": utilisateur.pseudo,
            }

    except HTTPException:
        raise
    except Exception as e:
        # Erreur inattendue
        print("DEBUG /me/update: exception inattendue", e)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la mise à jour du compte"
        )


@router.delete("/supprimer", tags=["Utilisateur"])
def supprimer_mon_compte(
    confirmation: str, utilisateur: Utilisateur = Depends(obtenir_utilisateur)
):
    """
    **Supprime le compte de l'utilisateur connecté et le déconnecte**

    ### Paramètre
    - **confirmation** *str* saisir 'CONFIRMER' pour valider la demande de suppression du compte

    ### Réponse
    Message de confirmation ou d'erreur
    """
    try:
        # On recupere l'ID avant suppression pour les logs
        id_utilisateur = utilisateur.id_utilisateur
        pseudo = utilisateur.pseudo

        if confirmation == "CONFIRMER":
            # appel du service pour supprimer le compte
            suppression_reussie = service_utilisateur.supprimer_utilisateur(utilisateur)

            if not suppression_reussie:
                raise HTTPException(
                    status_code=500, detail="Erreur lors de la suppression du compte"
                )

            return {
                "information": f"Le compte au nom de {pseudo}, associé à l'id {id_utilisateur} à été supprimé",
                "message": "Compte supprimé avec succès.",
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
