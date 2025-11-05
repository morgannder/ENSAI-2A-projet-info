# app_test_api.py
import os
from datetime import datetime, timedelta
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

# Mettre test_dao à false si tes avec la vrai bd
ResetDatabase().lancer(test_dao=True)

app = FastAPI(title="User Test API", version="1.0")

SECRET_KEY = "sssecretkey"  # pas a stocker là
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60000


#################### REMARQUE A rajouter dans APP FINALE

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

####################

# ---------------------------
# SERVICES
# ---------------------------
service = UtilisateurService()
cocktail_service = CocktailService()
service_utilisateur = UtilisateurService()
service_inventaire = InventaireService()


# ---------------------------
# MODELS
# ---------------------------
class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    pseudo: str
    mdp: str
    age: int
    langue: str  # "FR", "EN", "ES"


class Ingredient(BaseModel):
    nom_ingredient: str


class Reponse(BaseModel):
    confirmation: str


class UserUpdate(BaseModel):
    nouveau_pseudo: Optional[str] = None
    nouveau_mdp: Optional[str] = None
    langue: Optional[str] = None


class CocktailFilter(BaseModel):
    nom_cocktail: Optional[str] = None
    categorie: Optional[str] = None
    alcool: Optional[str] = None
    verre: Optional[str] = None
    ingredients: Optional[list[str]] = None


# ---------------------------
# UTILS TOKEN
# ---------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
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
        utilisateur = service.trouver_par_id(user_id)
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
        raise HTTPException(
            status_code=401,
            detail="Veuillez vous connecter pour pouvoir accéder à cette fonctionnalité.",
        )


#################### REMARQUE A rajouter dans APP FINALE


def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[Utilisateur]:
    """Retourne l'utilisateur courant s'il est authentifié, sinon est considéré comme visiteur."""
    if not token:
        print("DEBUG aucun token fourni → Visiteur")
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        utilisateur = service.trouver_par_id(int(user_id_str))
        print("DEBUG utilisateur optionnel trouvé:", utilisateur)
        return utilisateur
    except Exception as e:
        print("DEBUG erreur token optionnel:", e)
        return None


####################


@app.post("/token", response_model=Token, include_in_schema=False)
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    print("DEBUG /token: 22222 username =", form_data.username)
    print("DEBUG /token: mot de passsssssssssssssssssssssssss =", form_data.password)

    utilisateur = service.se_connecter(form_data.username, form_data.password)
    if not utilisateur:
        print("DEBUG échec connexion: identifiants incorrects")
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    print("DEBUG utilisateur connecté:", utilisateur)
    print("DEBUG /token: pseudo =", form_data.username, "mdp =", form_data.password)
    access_token = create_access_token(data={"sub": str(utilisateur.id_utilisateur)})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Modèle de requête pour l'inscription ---
LANGUES_VALIDES = {"string", "FRA", "ESP", "ITA", "ENG", "GER"}


@app.post("/inscription", tags=["Visiteur"])
def inscription(data: UserCreate):
    print("DEBUG /register: données reçues:", data)

    try:
        if data.langue not in LANGUES_VALIDES:
            raise HTTPException(
                status_code=400,
                detail=f"Langue '{data.langue}' non valide. Langues acceptées : {', '.join(sorted(LANGUES_VALIDES))}",
            )
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


@app.post("/mon_compte/deconnexion", tags=["Utilisateur"])
def deconnexion(tilisateur: Utilisateur = Depends(get_current_user)):
    return


@app.get("/mon_compte/informations", tags=["Utilisateur"])
def mes_informations(utilisateur: Utilisateur = Depends(get_current_user)):
    print("DEBUG /me appelé pour l'utilisateur:", utilisateur)

    return {
        "pseudo": utilisateur.pseudo,
        "age": utilisateur.age,
        "langue": utilisateur.langue,
        "est_majeur": utilisateur.est_majeur,
    }


@app.put("/mon_compte/mettre_a_jour", tags=["Utilisateur"])
def modifie_compte(data: UserUpdate, utilisateur: Utilisateur = Depends(get_current_user)):
    """Met à jour le compte de l'utilisateur connecté"""
    print("DEBUG /me/update: données reçues:", data)
    print("DEBUG /me/update: utilisateur avant update:", utilisateur)

    try:
        if data.nouveau_pseudo:
            succes = service_utilisateur.changer_pseudo(utilisateur, data.nouveau_pseudo)
            print("DEBUG changement pseudo:", succes)
            if not succes:
                raise HTTPException(status_code=400, detail="Pseudo déjà utilisé")

        if data.nouveau_mdp:
            succes = service_utilisateur.changer_mdp(utilisateur, data.nouveau_mdp)
            print("DEBUG changement mdp:", succes)
            if not succes:
                raise HTTPException(status_code=400, detail="Erreur changement mot de passe")

        if data.langue:
            succes = service_utilisateur.choisir_langue(utilisateur, data.langue)
            print("DEBUG changement langue:", succes)
            if not succes:
                raise HTTPException(status_code=400, detail="Erreur changement langue")

    except Exception as e:
        print("DEBUG /register: exception", e)
        raise HTTPException(
            status_code=500, detail="Erreur interne lors de la création utilisateur"
        )


@app.delete("/mon_compte/supprimer", tags=["Utilisateur"])
def supprimer_mon_compte(reponse: Reponse, utilisateur: Utilisateur = Depends(get_current_user)):
    """
    Supprime le compte de l'utilisateur connecté et le déconnecte
    """
    try:
        # Récupérer l'ID avant suppression pour les logs
        id_utilisateur = utilisateur.id_utilisateur
        pseudo = utilisateur.pseudo

        if reponse.confirmation == "CONFIRMER":
            # Appeler le service pour supprimer le compte
            suppression_reussie = service_utilisateur.supprimer_utilisateur(utilisateur)

            if not suppression_reussie:
                raise HTTPException(
                    status_code=500, detail="Erreur lors de la suppression du compte"
                )

            return {
                "information": f"Le compte au nom de {pseudo}, associé à l'id {id_utilisateur} à été supprimé",
                "message": "Compte supprimé avec succès. Vous avez été déconnecté.",
                "supprime": True,
            }
        else:
            raise HTTPException(
                status_code=409,
                detail="Erreur de conflit, vous devez taper CONFIRMER dans le champ de confirmation pour valider votre requête",
            )
    except Exception as e:
        print("DEBUG /register: exception", e)
        raise HTTPException(
            status_code=500, detail="Erreur interne lors de la création utilisateur"
        )


#################### REMARQUE A rajouter dans APP FINALE

# ===================  ENDPOINTS COCKTAILS  ==================================


@app.post(
    "/cocktails/recherche",
    tags=["Cocktails"],
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

        cocktails = cocktail_service.rechercher_par_filtre(
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


@app.get(
    "/cocktails/complets",
    tags=["Cocktails"],
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
        cocktails = cocktail_service.lister_cocktails_complets(
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


@app.get(
    "/cocktails/partiels",
    tags=["Cocktails"],
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
        cocktails = cocktail_service.lister_cocktails_partiels(
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


@app.get(
    "/cocktails/aleatoires",
    tags=["Cocktails"],
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

        cocktails = cocktail_service.cocktails_aleatoires(
            est_majeur=est_majeur, nb=nb, langue=langue
        )

        return {
            "total": len(cocktails),
            "resultats": [c.__dict__ for c in cocktails],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/cocktails/categories", tags=["Cocktails"])
def lister_categories():
    """
    **Lister les catégories de cocktails**

    Permet d'obtenir la liste complète des catégories présentes dans la base.
    """
    categories = cocktail_service.lister_categories()
    return {"categories": categories}


@app.get("/cocktails/verres", tags=["Cocktails"])
def lister_verres():
    """
    **Lister les types de verres**

    Permet d'obtenir la liste complète des types de verres présents dans la base.
    """
    verres = cocktail_service.lister_verres()
    return {"verres": verres}


# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
