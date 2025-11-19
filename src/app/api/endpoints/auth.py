from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from app.core.security import creation_token_d_acces, obtenir_utilisateur_optionnel
from business_object.utilisateur import Utilisateur
from service.utilisateur_service import UtilisateurService
from utils.reset_database import ResetDatabase

router = APIRouter(tags=["Authentification"])
service_utilisateur = UtilisateurService()


class UserCreate(BaseModel):
    pseudo: str = Field(..., description="Votre pseudo (doit être unique)")
    mdp: str = Field(..., description="Votre mot de passe")
    age: int = Field(
        ...,
        description="Votre âge (doit être compris entre 13 et 130 pour accéder à l'intégralité de l'application)",
    )
    langue: str = Field(
        ...,
        description=(
            "Langue de l'utilisateur. Valeurs possibles : "
            "'string' (anglais par défaut), 'FRA' (français), 'ESP' (espagnol), "
            "'ITA' (italien), 'ENG' (anglais), 'GER' (allemand)"
        ),
    )


class Token(BaseModel):
    access_token: str
    token_type: str


Base = Literal["Test", "Prod"]
LANGUES_VALIDES = {"string", "FRA", "ESP", "ITA", "ENG", "GER"}


@router.post("/token", response_model=Token, include_in_schema=False)
def token(form_donnee: OAuth2PasswordRequestForm = Depends()):
    print("DEBUG /token: username =", form_donnee.username)
    utilisateur = service_utilisateur.se_connecter(
        form_donnee.username, form_donnee.password
    )

    if not utilisateur:
        print("DEBUG échec connexion: identifiants incorrects")
        raise HTTPException(status_code=401, detail="Identifiants incorrects")

    print("DEBUG utilisateur connecté:", utilisateur)
    print("DEBUG /token: pseudo =", form_donnee.username, "mdp =", form_donnee.password)
    access_token = creation_token_d_acces(
        donnee={"sub": str(utilisateur.id_utilisateur)}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/inscription")
def inscription(
    donnee: UserCreate,
    utilisateur_connecte: Optional[Utilisateur] = Depends(
        obtenir_utilisateur_optionnel
    ),
):
    """
    **Créer un nouveau compte utilisateur**

    Pour vous inscrire, remplissez les champs suivants :

    - **pseudo** *(string)* → votre pseudo, doit contenir au moins 3 charactères
    - **mdp** *(string)* → Votre mot de passe. Il doit respecter les règles de sécurité suivantes :
        - Au moins 8 caractères
        - Au moins une lettre majuscule
        - Au moins une lettre minuscule
        - Au moins un chiffre
        - Au moins un caractère spécial (ex: !@#$%^&*)
    - **age** *(int)* → votre âge (doit être compris entre **13 et 130** pour accéder à l'intégralité de notre application)
    - **langue** *(string)* → langue pour les recettes, doit être l’une des valeurs suivantes :
      - `"string"` (anglais par défaut)
      - `"FRA"` (français)
      - `"ESP"` (espagnol)
      - `"ITA"` (italien)
      - `"ENG"` (anglais)
      - `"GER"` (allemand)
    """
    # empêche l'utilisateur connecté d'avoir accès à la création d'un nouveau compte
    if utilisateur_connecte:
        raise HTTPException(
            status_code=403,
            detail="Vous êtes déjà connecté, vous ne pouvez pas créer un nouveau compte.",
        )

    print("DEBUG /register: données reçues:", donnee)
    print("DEBUG: langue reçue =", donnee.langue)
    print("DEBUG: langues valides =", LANGUES_VALIDES)
    print("DEBUG: test langue valide =", donnee.langue in LANGUES_VALIDES)

    try:
        # Vérification de tous les cas d'erreurs (sauf du mdp qui ets géré dans le service)
        if donnee.langue not in LANGUES_VALIDES:
            raise HTTPException(
                status_code=400,
                detail=f"Langue '{donnee.langue}' non valide. Langues acceptées : {', '.join(sorted(LANGUES_VALIDES))}",
            )
        if donnee.age < 13 or donnee.age > 130:
            raise HTTPException(
                status_code=400,
                detail=f"L'âge '{donnee.age}' n'est pas valide. Il doit être compris entre 13 et 130 ans.",
            )
        if len(donnee.pseudo) < 3:
            raise HTTPException(
                status_code=400, detail="Le pseudo doit contenir au moins 3 charactères"
            )
        # Appel de la méthode existante du service
        utilisateur = service_utilisateur.creer_utilisateur(
            pseudo=donnee.pseudo,
            mdp=donnee.mdp,  # mot de passe en clair, la méthode hash
            age=donnee.age,
            langue=donnee.langue,
            cocktails_recherches=0,
        )
        if not utilisateur:
            print(utilisateur)
            print("DEBUG /register: pseudo déjà utilisé ou erreur création")
            raise HTTPException(
                status_code=400, detail="Pseudo déjà utilisé ou erreur création"
            )

        # Génération du token JWT pour l'utilisateur créé
        token = creation_token_d_acces(donnee={"sub": str(utilisateur.id_utilisateur)})
        print("DEBUG /register: utilisateur créé, token =", token)

        return {
            "message": "Utilisateur créé",
            "pseudo": utilisateur.pseudo,
            "id": utilisateur.id_utilisateur,
            "access_token": token,
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except Exception as e:
        print("DEBUG /register: exception", e)
        raise HTTPException(
            status_code=500, detail="Erreur interne lors de la création utilisateur"
        )


@router.post("/changement_base")
def changement_base(
    base_test: Base,
    utilisateur_connecte: Optional[Utilisateur] = Depends(
        obtenir_utilisateur_optionnel
    ),
):
    """
    **Permet à un administrateur (ici les comptes "a" et "admin") de changer de base de données,
    cette fonctionnalité permet de passer d'une base à l'autre facilement sans avoir à redémarrer
    main.py et changer le fichier config.py**

    - **Base_test** *Literal* à choisir parmi Test ou Prod

    """

    if utilisateur_connecte is not None and utilisateur_connecte.pseudo in [
        "a",
        "admin",
    ]:
        if base_test == "Test":
            ResetDatabase().lancer(test_dao=True)
            return {"message": "Tu es sur la base test"}
        else:
            ResetDatabase().lancer(test_dao=False)
            return {"message": "Tu es sur la base prod"}
    else:
        return {"message": "Tu n'as pas les permissions nécessaires"}
