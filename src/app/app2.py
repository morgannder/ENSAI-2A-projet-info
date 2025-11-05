# app_test_api.py
import os
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

import dotenv
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, conint

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


class Filtres(BaseModel):
    Alcool: Optional[str] = None


class CocktailFilter(BaseModel):
    nom_cocktail: Optional[str] = None
    categorie: Optional[str] = None
    alcool: Optional[str] = None
    verre: Optional[str] = None
    ingredients: Optional[list[str]] = None


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
LANGUES_VALIDES = {"string", "FRA", "ESP", "ITA", "ENG", "GER"}


class UserCreate(BaseModel):
    pseudo: str = Field(..., description="Votre pseudo")
    mdp: str = Field(..., description="Votre mot de passe")
    age: conint(ge=13, le=130) = Field(
        ...,
        description="Votre âge (doit être compris entre 13 et 130 pour accéder à l'intégralité de l'application)",
    )
    langue: Literal["string", "FRA", "ESP", "ITA", "ENG", "GER"] = Field(
        "string",
        description=(
            "Langue de l'utilisateur. Valeurs possibles : "
            "'string' (anglais par défaut), 'FRA' (français), 'ESP' (espagnol), "
            "'ITA' (italien), 'ENG' (anglais), 'GER' (allemand)"
        ),
    )


class Ingredient(BaseModel):
    nom_ingredient: str


class Reponse(BaseModel):
    confirmation: str


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
    """
    **Créer un nouveau compte utilisateur**

    Pour vous inscrire, remplissez les champs suivants :

    - **pseudo** *(string)* → votre pseudo
    - **mdp** *(string)* → votre mot de passe
    - **age** *(int)* → votre âge (doit être compris entre **13 et 130** pour accéder à l'intégralité de notre application)
    - **langue** *(string)* → langue de l’utilisateur, doit être l’une des valeurs suivantes :
      - `"string"` (anglais par défaut)
      - `"FRA"` (français)
      - `"ESP"` (espagnol)
      - `"ITA"` (italien)
      - `"ENG"` (anglais)
      - `"GER"` (allemand)
    """
    print("DEBUG /register: données reçues:", data)
    print("DEBUG: langue reçue =", data.langue)
    print("DEBUG: langues valides =", LANGUES_VALIDES)
    print("DEBUG: test langue valide =", data.langue in LANGUES_VALIDES)

    try:
        if data.langue not in LANGUES_VALIDES:
            raise HTTPException(
                status_code=400,
                detail=f"Langue '{data.langue}' non valide. Langues acceptées : {', '.join(sorted(LANGUES_VALIDES))}",
            )
        if data.age < 13 or data.age > 130:
            raise HTTPException(
                status_code=400,
                detail=f"L'âge '{data.age}' n'est pas valide. Il doit être compris entre 13 et 130 ans.",
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
    except HTTPException:
        raise
    except Exception as e:
        print("DEBUG /register: exception", e)
        raise HTTPException(
            status_code=500, detail="Erreur interne lors de la création utilisateur"
        )


# ---------------------------
# Utilisateur
# ---------------------------


@app.get("/mon_compte/informations", tags=["Utilisateur"])
def mes_informations(utilisateur: Utilisateur = Depends(get_current_user)):
    """
    **Visualiser les informations de votre compte**

    Comprends les champs suivants :

    - **pseudo** → votre pseudo
    - **age** → votre âge
    - **langue**  → langue choisie
    """
    print("DEBUG /me appelé pour l'utilisateur:", utilisateur)

    return {
        "pseudo": utilisateur.pseudo,
        "age": utilisateur.age,
        "langue": utilisateur.langue,
        "date_creation": utilisateur.date_creation.isoformat(),
    }


@app.put("/mon_compte/mettre_a_jour", tags=["Utilisateur"])
def modifie_compte(data: UserUpdate, utilisateur: Utilisateur = Depends(get_current_user)):
    print("DEBUG /me/update: données reçues:", data)
    print("DEBUG /me/update: utilisateur avant update:", utilisateur)

    changements = []

    try:
        if data.nouveau_pseudo:
            if data.nouveau_pseudo == utilisateur.pseudo:
                raise HTTPException(
                    status_code=400, detail="Le nouveau pseudo est identique à l'ancien"
                )
            succes = service_utilisateur.changer_pseudo(utilisateur, data.nouveau_pseudo)
            if not succes:
                raise HTTPException(status_code=400, detail="Pseudo déjà utilisé")
            changements.append("pseudo")

        if data.nouveau_mdp:
            resultat = service_utilisateur.changer_mdp(utilisateur, data.nouveau_mdp)
            if resultat == "identique":
                raise HTTPException(
                    status_code=400,
                    detail="Le nouveau mot de passe est identique à l'ancien",
                )
            elif resultat == "erreur":
                raise HTTPException(
                    status_code=500,
                    detail="Erreur interne lors du changement de mot de passe",
                )
            else:
                changements.append("mot de passe")

        if data.langue:
            succes = service_utilisateur.choisir_langue(utilisateur, data.langue)
            if not succes:
                raise HTTPException(
                    status_code=400,
                    detail=f"Langue '{data.langue}' non valide. Langues acceptées : {', '.join(sorted(LANGUES_VALIDES))}",
                )
            changements.append("langue")

        if not changements:
            raise HTTPException(status_code=400, detail="Aucune modification fournie")

        return {
            "message": f"Modification réussie : {', '.join(changements)}",
            "utilisateur": utilisateur.pseudo,
        }

    except HTTPException:
        raise
    except Exception as e:
        print("DEBUG /register: exception", e)
        raise HTTPException(
            status_code=500, detail="Erreur interne lors de la mise à jour utilisateur"
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
            status_code=500, detail="Erreur interne lors de la création utilisateur"
        )


# ---------------------------
# Inventaire
# ---------------------------
@app.get("/inventaire/vue", tags=["Inventaire"])
def consulte_inventaire(utilisateur: Utilisateur = Depends(get_current_user)):
    """Montre l'inventaire de l'utilisateur"""
    try:
        return service_inventaire.lister(utilisateur.id_utilisateur)

    except Exception as e:
        print("DEBUG /inventaire/vue: exception", e)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la visualisation de l'inventaire",
        )


@app.get(
    "/ingredients/suggestion",
    tags=["Inventaire"],
    responses={
        200: {"description": "Sélection aléatoire de cocktails."},
        400: {"description": "Paramètre invalide."},
    },
)
def suggestion_ingredients(n: int = 5):
    """
    Retourne jusqu'à n ingrédients au hasard pour aider l'utilisateur.
    Limité entre 1 et 10.
    """
    suggestions = service_inventaire.suggerer_ingredients(n)
    return [ing.nom_ingredient for ing in suggestions]


@app.put("/inventaire/ajouter", tags=["Inventaire"])
def ajoute_ingredient(
    demande_ingredient: str, utilisateur: Utilisateur = Depends(get_current_user)
):
    """Ajoute un ingrédient à l'inventaire de l'utilisateur"""
    try:
        requete = service_inventaire.recherche_ingredient(demande_ingredient)
        return service_inventaire.ajouter(utilisateur.id_utilisateur, requete)

    except Exception as e:
        print("DEBUG /inventaire/vue: exception", e)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la visualisation de l'inventaire",
        )


@app.delete("/inventaire/supprimer", tags=["Inventaire"])
def supprime_ingredient(
    demande_ingredient: str, utilisateur: Utilisateur = Depends(get_current_user)
):
    """Supprime un ingrédient à l'inventaire de l'utilisateur"""
    try:
        requete = service_inventaire.recherche_ingredient(demande_ingredient)
        return service_inventaire.supprimer(utilisateur.id_utilisateur, requete.id_ingredient)

    except Exception as e:
        print("DEBUG /inventaire/vue: exception", e)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la visualisation de l'inventaire",
        )


# ---------------------------
# Cocktails
# ---------------------------


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
        utilisateur = service_utilisateur.trouver_par_id(int(user_id_str))
        print("DEBUG utilisateur optionnel trouvé:", utilisateur)
        return utilisateur
    except Exception as e:
        print("DEBUG erreur token optionnel:", e)
        return None


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

        cocktails = service_cocktail.rechercher_par_filtre(
            est_majeur=est_majeur,
            nom_cocktail=filtres.nom_cocktail,
            categ=filtres.categorie,
            alcool=filtres.alcool,
            liste_ingredients=filtres.ingredients,
            verre=filtres.verre,
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
    try:
        cocktails = service_cocktail.lister_cocktails_complets(
            id_utilisateur=utilisateur.id_utilisateur,
            est_majeur=utilisateur.est_majeur,
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
    try:
        cocktails = service_cocktail.lister_cocktails_partiels(
            nb_manquants=nb_manquants,
            id_utilisateur=utilisateur.id_utilisateur,
            est_majeur=utilisateur.est_majeur,
            limit=limit,
            offset=offset,
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
    try:
        # Si pas connecté → pas de restriction (None)
        est_majeur = utilisateur.est_majeur if utilisateur else None

        cocktails = service_cocktail.cocktails_aleatoires(est_majeur=est_majeur, nb=nb)

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
    categories = service_cocktail.lister_categories()
    return {"categories": categories}


@app.get("/cocktails/verres", tags=["Cocktails"])
def lister_verres():
    """
    **Lister les types de verres**

    Permet d'obtenir la liste complète des types de verres présents dans la base.
    """
    verres = service_cocktail.lister_verres()
    return {"verres": verres}


# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
