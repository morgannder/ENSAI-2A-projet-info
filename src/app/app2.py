# app_test_api.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import dotenv
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from business_object.utilisateur import Utilisateur
from service.cocktail_service import CocktailService
from service.inventaire_service import InventaireService
from service.utilisateur_service import UtilisateurService
from utils.reset_database import ResetDatabase

# ---------------------------
# CONFIG API
# ---------------------------
dotenv.load_dotenv()
os.environ["POSTGRES_SCHEMA"] = "projet_test_dao"  # utilisation de la bdd test
ResetDatabase().lancer(test_dao=True)

app = FastAPI(title="User Test API", version="1.0")

SECRET_KEY = "sssecretkey"  # pas a stocker là
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60000

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

service_utilisateur = UtilisateurService()
service_inventaire = InventaireService()
service_cocktail = CocktailService()


# ---------------------------
# MODELS
# ---------------------------
class Token(BaseModel):
    access_token: str
    token_type: str


class UserUpdate(BaseModel):
    nouveau_pseudo: Optional[str] = None
    nouveau_mdp: Optional[str] = None
    langue: Optional[str] = None


# ---------------------------
# UTILS TOKEN AVEC TRACE
# ---------------------------


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    print("DEBUG token créé:", token)
    return token


def get_current_user(token: str = Depends(oauth2_scheme)) -> Utilisateur:
    print("DEBUG get_current_user: token reçu:", token)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("DEBUG payload JWT:", payload)
        user_id_str = payload.get("sub")
        if not user_id_str:
            print("DEBUG erreur: pas d'id dans le token")
            raise HTTPException(status_code=401, detail="Token invalide : pas d'id")

        user_id = int(user_id_str)
        print("DEBUG user_id extrait:", user_id)
        utilisateur = service_utilisateur.trouver_par_id(user_id)
        print("DEBUG utilisateur trouvé:", utilisateur)

        if not utilisateur:
            print("DEBUG utilisateur introuvable pour cet id")
            raise HTTPException(status_code=404, detail="Utilisateur introuvable")

        return utilisateur

    except jwt.ExpiredSignatureError:
        print("DEBUG token expiré")
        raise HTTPException(status_code=401, detail="Token expiré")

    except Exception as e:
        print("DEBUG erreur lors du décodage du token:", e)
        raise HTTPException(status_code=401, detail="Token invalide")


# ---------------------------
# ROUTES AVEC TRACE
# ---------------------------


# --- Modèle de requête pour l'inscription ---
class UserCreate(BaseModel):
    pseudo: str
    mdp: str
    age: int
    langue: str  # "FR", "EN", "ES"


# --- Route d'inscription ---


@app.post("/token", response_model=Token, include_in_schema=False)
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    print("DEBUG /token: username =", form_data.username)
    utilisateur = service_utilisateur.se_connecter(form_data.username, form_data.password)

    if not utilisateur:
        print("DEBUG échec connexion: identifiants incorrects")
        raise HTTPException(status_code=401, detail="Identifiants incorrects")

    print("DEBUG utilisateur connecté:", utilisateur)
    print("DEBUG /token: pseudo =", form_data.username, "mdp =", form_data.password)
    access_token = create_access_token(data={"sub": str(utilisateur.id_utilisateur)})

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/inscription", tags=["Visiteur"])
def inscription(data: UserCreate):
    print("DEBUG /register: données reçues:", data)

    try:
        # Appel de la méthode existante du service
        utilisateur = service_utilisateur.creer_utilisateur(
            pseudo=data.pseudo,
            mdp=data.mdp,  # mot de passe en clair, la méthode hash
            age=data.age,
            langue=data.langue,
            est_majeur=None,  # sera recalculé dans la méthode
        )
        if not utilisateur:
            print(utilisateur)
            print("DEBUG /register: pseudo déjà utilisé ou erreur création")
            raise HTTPException(status_code=400, detail="Pseudo déjà utilisé ou erreur création")

        # Génération du token JWT pour l'utilisateur créé
        token = create_access_token(data={"sub": str(utilisateur.id_utilisateur)})
        print("DEBUG /register: utilisateur créé, token =", token)

        return {
            "message": "Utilisateur créé",
            "pseudo": utilisateur.pseudo,
            "id": utilisateur.id_utilisateur,
            "access_token": token,
            "token_type": "bearer",
        }

    except Exception as e:
        print("DEBUG /register: exception", e)
        raise HTTPException(
            status_code=500, detail="Erreur interne lors de la création utilisateur"
        )


@app.post("/connexion", tags=["Visiteur"])
def connexion(data):
    return


# ---------------------------
# Utilisateur
# ---------------------------


@app.post("/deconnexion", tags=["Utilisateur"])
def deconnexion(tilisateur: Utilisateur = Depends(get_current_user)):
    return


@app.get("/moi/compte", tags=["Utilisateur"])
def mes_informations(utilisateur: Utilisateur = Depends(get_current_user)):
    print("DEBUG /me appelé pour l'utilisateur:", utilisateur)

    return {
        "pseudo": utilisateur.pseudo,
        "age": utilisateur.age,
        "langue": utilisateur.langue,
        "est_majeur": utilisateur.est_majeur,
    }


@app.put("/moi/mise_a_jour", tags=["Utilisateur"])
def modifie_compte(data: UserUpdate, utilisateur: Utilisateur = Depends(get_current_user)):
    """Met à jour le compte de l'utilisateur connecté"""
    return


@app.delete("/moi/supprimer", tags=["Utilisateur"])
def supprime_compte(utilisateur: Utilisateur = Depends(get_current_user)):
    """Supprime le compte de l'utilisateur connecté"""
    return


# ---------------------------
# Inventaire
# ---------------------------
@app.get("/inventaire/vue", tags=["Inventaire"])
def consulte_inventaire(utilisateur: Utilisateur = Depends(get_current_user)):
    """Montre l'inventaire de l'utilisateur"""

    return service_inventaire.consulter_inventaire(utilisateur.id_utilisateur)


@app.put("/inventaire/ajoute", tags=["Inventaire"])
def ajoute_ingredient(ingredient, utilisateur: Utilisateur = Depends(get_current_user)):
    """ajoute un ingrédient à l'inventaire de l'utilisateur"""

    return


@app.delete("/inventaire/supprime", tags=["Inventaire"])
def supprime_ingredient(ingredient, utilisateur: Utilisateur = Depends(get_current_user)):
    """ajoute un ingrédient à l'inventaire de l'utilisateur"""

    return


# ---------------------------
# Cocktails
# ---------------------------
@app.get("/cocktail/recherche_filtre", tags=["Cocktail"])
def recherche_par_filtre(data):
    """
    Recherche les cocktails via un filtre établi.
    """
    return


@app.get("/cocktail/realisable", tags=["Cocktail"])
def lister_cocktails_complets(data, utilisateur: Utilisateur = Depends(get_current_user)):
    """
    Recherche les cocktails via un filtre établi.
    """
    return


@app.get("/cocktail/partiel", tags=["Cocktail"])
def lister_cocktails_partiels(data, utilisateur: Utilisateur = Depends(get_current_user)):
    """
    Recherche les cocktails via un filtre établi.
    """
    return


# update mais focntionne pas bien (update specifique pour chaque cas)

""" @app.put("/me/update", tags=["Utilisateur"])
def update_my_info(
    data: UserUpdate,
    utilisateur: Utilisateur = Depends(get_current_user)
):
    print("DEBUG /me/update: données reçues:", data)
    print("DEBUG /me/update: utilisateur avant update:", utilisateur)

    if data.nouveau_pseudo:
        ok = service.changer_pseudo(utilisateur, data.nouveau_pseudo)
        print("DEBUG changement pseudo:", ok)
        if not ok:
            raise HTTPException(status_code=400, detail="Pseudo déjà utilisé")

    if data.nouveau_mdp:
        ok = service.changer_mdp(utilisateur, data.nouveau_mdp)
        print("DEBUG changement mdp:", ok)
        if not ok:
            raise HTTPException(status_code=400, detail="Erreur changement mot de passe")

    if data.langue:
        ok = service.choisir_langue(utilisateur, data.langue)
        print("DEBUG changement langue:", ok)
        if not ok:
            raise HTTPException(status_code=400, detail="Erreur changement langue")

    # Générer un nouveau token après mise à jour
    new_token = create_access_token(data={"sub": str(utilisateur.id_utilisateur)})
    print("DEBUG /me/update: nouvel utilisateur et token:", utilisateur, new_token)
    print("DEBUG mot de passe stocké:", service.trouver_par_id(utilisateur.id_utilisateur).mdp)


    return {
        "message": "Informations mises à jour",
        "pseudo": utilisateur.pseudo,
        "access_token": new_token
    } """


# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
