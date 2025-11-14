from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from business_object.utilisateur import Utilisateur
from service.utilisateur_service import UtilisateurService

from .config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)
service_utilisateur = UtilisateurService()


def creation_token_d_acces(donnee: dict, temps_expiration: Optional[timedelta] = None):
    """
    Créer un token d'accès pour les utilisateurs avec un temps de validité limité

    ### Paramètres
    - **donnee** *dict*
    - **validite** *timedelta* Temps de validité du token, 10080 minutes = 1 semaine

    ### Retour
    token

    """
    a_encoder = donnee.copy()
    expiration = datetime.now(timezone.utc) + (
        temps_expiration or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    a_encoder.update({"exp": expiration})
    token = jwt.encode(a_encoder, SECRET_KEY, algorithm=ALGORITHM)

    print("DEBUG token créé:", token)
    return token


def obtenir_utilisateur(token: str = Depends(oauth2_scheme)) -> Utilisateur:
    """
    Obtiens un utilisateur via son token d'accès

    ### Paramètres
    - **token** *str* Token de l'utilisateur

    ### Retour
    Utilisateur

    """
    try:
        donnees_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_utilisateur = int(donnees_token.get("sub"))
        utilisateur = service_utilisateur.trouver_par_id(id_utilisateur)
        if not utilisateur:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable")
        return utilisateur
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Veuillez vous connecter pour pouvoir accéder à cette fonctionnalité.",
        )


def obtenir_utilisateur_optionnel(token: str = Depends(oauth2_scheme)) -> Utilisateur | None:
    """
    Obtiens un utilisateur via son token d'accès, permet de faire une situation où le client
    n'a pas la nécessité d'être connecté mais a des fonctionnalités en plus s'il l'est

    ### Paramètres
    - **token** *str* Token de l'utilisateur

    ### Retour
    Utilisateur | None

    """
    if not token:
        return None
    try:
        donnees_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_utilisateur = int(donnees_token.get("sub"))
        return service_utilisateur.trouver_par_id(id_utilisateur)
    except Exception:
        return None
