from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import obtenir_utilisateur, obtenir_utilisateur_optionnel
from business_object.utilisateur import Utilisateur
from service.cocktail_service import CocktailService
from service.utilisateur_service import UtilisateurService

service_cocktail = CocktailService()
service_utilisateur = UtilisateurService()

router = APIRouter(tags=["Cocktails"])


class CocktailFilter(BaseModel):
    nom_cocktail: Optional[str] = None
    categorie: Optional[str] = None
    alcool: Optional[str] = None
    verre: Optional[str] = None
    ingredients: Optional[list[str]] = None


Alcool = Literal["Alcoholic", "Non alcoholic", "Optional Alcohol"]
Number = Literal["1", "2", "3", "4", "5"]
Categories = Literal[
    "Beer",
    "Cocktail",
    "Cocoa",
    "Coffee / Tea",
    "Homemade Liqueur",
    "Ordinary Drink",
    "Other / Unknown",
    "Punch / Party Drink",
    "Shake",
    "Shot",
    "Soft Drink",
]

Verres = Literal[
    "Balloon Glass",
    "Beer Glass",
    "Beer mug",
    "Beer pilsner",
    "Brandy snifter",
    "Champagne flute",
    "Champagne Flute",
    "Cocktail glass",
    "Cocktail Glass",
    "Coffee mug",
    "Coffee Mug",
    "Collins glass",
    "Collins Glass",
    "Copper Mug",
    "Cordial glass",
    "Coupe Glass",
    "Highball glass",
    "Highball Glass",
    "Hurricane glass",
    "Irish coffee cup",
    "Jar",
    "Margarita glass",
    "Margarita/Coupette glass",
    "Martini Glass",
    "Mason jar",
    "Nick and Nora Glass",
    "Old-fashioned glass",
    "Old-Fashioned glass",
    "Parfait glass",
    "Pint glass",
    "Pitcher",
    "Pousse cafe glass",
    "Punch bowl",
    "Punch Bowl",
    "Shot glass",
    "Shot Glass",
    "Whiskey Glass",
    "Whiskey sour glass",
    "White wine glass",
    "Wine Glass",
]


# ------------------- Endpoint: /cocktails/details -----------------------------


@router.post(
    "/realiser_cocktail",
    tags=["Cocktails"],
    responses={
        200: {"description": "Détails complets du cocktail 🍹"},
        400: {"description": "Paramètres invalides"},
        404: {"description": "Cocktail introuvable"},
    },
)
def realiser_cocktail(
    id_cocktail: Optional[int] = None,
    nom_cocktail: Optional[str] = None,
    utilisateur: Optional[Utilisateur] = Depends(obtenir_utilisateur_optionnel),
):
    """
    ## 🍸 Obtenir la recette complète d'un cocktail

    Retrouvez toutes les informations d'un cocktail : instructions détaillées,
    catégorie, type de verre, et plus encore !

    ### ⚠️ L'abus d'alcool est dangereux pour la santé, à consommer avec modération


    ### 🔍 Comment Trouver votre cocktail ?
    Vous pouvez rechercher un cocktail de deux façons :
    - Par **ID** : `id_cocktail=123`
    - Ou par **nom** : `nom_cocktail=Margarita`

    ### 🌍 Langues disponibles
    Les instructions sont automatiquement affichées dans votre langue préférée
    si vous êtes connecté.

    """

    if id_cocktail is None and not nom_cocktail:
        raise HTTPException(
            status_code=400,
            detail="Veuillez fournir soit un 'id_cocktail' (nombre entier), soit un 'nom_cocktail' pour rechercher un cocktail.",
        )

    # Déterminer la langue
    langue = utilisateur.langue if utilisateur else "ENG"

    try:
        cocktail = service_cocktail.realiser_cocktail(
            id_cocktail=id_cocktail, nom_cocktail=nom_cocktail, langue=langue
        )

        if cocktail:
            service_utilisateur.ajout_cocktail_recherche(utilisateur)

            ingredients_liste = cocktail.ingredients.split("|||") if cocktail.ingredients else []
            quantites_liste = cocktail.quantites.split("|||") if cocktail.quantites else []

            ingredients_detailles = [
                {"ingredient": ing, "quantite": qty}
                for ing, qty in zip(ingredients_liste, quantites_liste)
            ]
        else:
            ingredients_detailles = []

        return {
            "cocktail": {
                "id": cocktail.id_cocktail,
                "nom": cocktail.nom_cocktail,
                "ingredients": ingredients_detailles,
                "instructions": cocktail.instruc_cocktail,
                "categorie": cocktail.categ_cocktail,
                "verre": cocktail.verre,
                "alcoolise": cocktail.alcoolise_cocktail,
                "image": cocktail.image_cocktail,
            },
            "message": f"🍹 Voici comment préparer un délicieux {cocktail.nom_cocktail} ☝️🤤!",
        }

    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="😔 Désolé, nous n'avons pas trouvé ce cocktail. Vérifiez l'id , l'orthographe du nom ou essayez un autre chose !",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")


# ------------------- Endpoint: /cocktails/recherche -----------------------------


@router.post(
    "/recherche",
    responses={
        200: {"description": "Liste de cocktails correspondant à vos critères."},
        400: {"description": "Paramètres invalides."},
        500: {"description": "Erreur serveur."},
    },
)
def rechercher_cocktails(
    limit: int = 10,
    offset: int = 0,
    nom_cocktail: Optional[str] = None,
    categorie: Optional[Categories] = None,
    alcool: Optional[Alcool] = None,
    verre: Optional[Verres] = None,
    ingredients: Optional[list[str]] = None,
    utilisateur: Optional[Utilisateur] = Depends(obtenir_utilisateur_optionnel),
):
    """
    **Rechercher des cocktails selon vos préférences**

    ### ⚠️ L'abus d'alcool est dangereux pour la santé, à consommer avec modération


    Vous pouvez filtrer par :
    - Nom du cocktail   (ex: `"Margarita"`)
    - Type d'alcool     *Literal* Sélectionnable ou None
    - Catégorie         *Literal* Sélectionnable ou None
    - Verre             *Literal* Sélectionnable ou None
    - Ingrédients       (ex: `["Tequila", "Citron"]`)

    Si vous n'êtes pas connecté, la recherche se fera sans restrictions d'âge.
    Si vous êtes mineur connecté, seuls les cocktails non alcoolisés seront affichés.

    """
    try:
        # Si pas connecté → pas de restriction (None)
        est_majeur = utilisateur.est_majeur if utilisateur else None

        if utilisateur:
            langue = utilisateur.langue
            service_utilisateur.ajout_cocktail_recherche(utilisateur)
        else:
            langue = "ENG"

        cocktails = service_cocktail.rechercher_par_filtre(
            est_majeur=est_majeur,
            nom_cocktail=nom_cocktail,
            categ=categorie,
            alcool=alcool,
            liste_ingredients=ingredients,
            verre=verre,
            langue=langue,
            limit=limit,
            offset=offset,
        )

        id_cocktails = [cocktail.id_cocktail for cocktail in cocktails]

        # Récupérer les ingrédients en une seule requête
        ingredients_par_cocktail = service_cocktail.obtenir_ingredients_par_cocktails(id_cocktails)

        # Construire la réponse avec les ingrédients
        resultats = []
        for cocktail in cocktails:
            cocktail_dict = cocktail.__dict__
            # Ajouter les ingrédients au résultat
            cocktail_dict["ingredients"] = ingredients_par_cocktail.get(cocktail.id_cocktail, [])
            resultats.append(cocktail_dict)

        return {
            "pagination": {"limit": limit, "offset": offset, "total": len(cocktails)},
            "resultats": resultats,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")


# ------------------- Endpoint: /cocktails/complets -----------------------------


@router.get(
    "/complets",
    responses={
        200: {"description": "Liste des cocktails réalisables à 100%."},
        401: {"description": "Vous devez être connecté."},
    },
)
def lister_cocktails_complets(
    limit: int = 10,
    offset: int = 0,
    utilisateur: Utilisateur = Depends(obtenir_utilisateur),
):
    """
    **Lister les cocktails que vous pouvez réaliser complètement**

    Nécessite d'être connecté pour accéder à votre inventaire.

    ### Paramètres de requête
    - **limit**     *(int, optionnel)* : Nombre maximum de cocktails à renvoyer (défaut 10).
    - **offset**    *(int, optionnel)* : Décalage pour la pagination.
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
        id_cocktails = [cocktail.id_cocktail for cocktail in cocktails]

        # Récupérer les ingrédients en une seule requête
        ingredients_par_cocktail = service_cocktail.obtenir_ingredients_par_cocktails(id_cocktails)

        # Construire la réponse avec les ingrédients
        resultats = []
        for cocktail in cocktails:
            cocktail_dict = cocktail.__dict__
            # Ajouter les ingrédients au résultat
            cocktail_dict["ingredients"] = ingredients_par_cocktail.get(cocktail.id_cocktail, [])
            resultats.append(cocktail_dict)

        return {
            "pagination": {"limit": limit, "offset": offset, "total": len(cocktails)},
            "resultats": resultats,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ------------------- Endpoint: /cocktails/partiels -----------------------------


@router.get(
    "/partiels",
    responses={
        200: {"description": "Liste des cocktails presque réalisables."},
        400: {"description": "Nombre d'ingrédients manquants invalide."},
        401: {"description": "Vous devez être connecté."},
    },
)
def lister_cocktails_partiels(
    nb_manquants: Number,
    limit: int = 10,
    offset: int = 0,
    utilisateur: Utilisateur = Depends(obtenir_utilisateur),
):
    """
    **Lister les cocktails presque réalisables**

    Nécessite d'être connecté pour accéder à votre inventaire.

    ### Paramètres de requête
    - **nb_manquants**  *Literal* : Nombre maximal d'ingrédients manquants autorisés (1-5).
    - **limit**         *(int, optionnel)* : Nombre maximum de cocktails à renvoyer.
    - **offset**        *(int, optionnel)* : Pagination.
    """
    if utilisateur:
        langue = utilisateur.langue
    else:
        langue = "ENG"
    try:
        cocktails = service_cocktail.lister_cocktails_partiels(
            nb_manquants=int(nb_manquants),
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
        id_cocktails = [cocktail.id_cocktail for cocktail in cocktails]

        # Récupérer tous les ingrédients des cocktails
        tous_ingredients = service_cocktail.obtenir_ingredients_par_cocktails(id_cocktails)

        # Récupérer les ingrédients possédés par l'utilisateur depuis l'inventaire
        ingredients_possedes_par_cocktail = (
            service_cocktail.obtenir_ingredients_possedes_par_cocktails(
                id_utilisateur=utilisateur.id_utilisateur, id_cocktails=id_cocktails
            )
        )

        # Construire la réponse avec les deux listes
        resultats = []
        for cocktail in cocktails:
            cocktail_dict = cocktail.__dict__
            id_cocktail = cocktail.id_cocktail

            # Tous les ingrédients du cocktail
            tous_ingredients_cocktail = tous_ingredients.get(id_cocktail, [])
            # Ingrédients que l'utilisateur possède (depuis l'inventaire)
            ingredients_possedes = ingredients_possedes_par_cocktail.get(id_cocktail, [])
            # Ingrédients manquants
            ingredients_manquants = [
                ing for ing in tous_ingredients_cocktail if ing not in ingredients_possedes
            ]

            # Ajouter les deux listes au résultat
            cocktail_dict["ingredients_possedes"] = ingredients_possedes
            cocktail_dict["ingredients_manquants"] = ingredients_manquants

            resultats.append(cocktail_dict)

        return {
            "pagination": {"limit": limit, "offset": offset, "total": len(cocktails)},
            "resultats": resultats,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ------------------- Endpoint: /cocktails/aleatoires -----------------------------


@router.get(
    "/aleatoires",
    responses={
        200: {"description": "Sélection aléatoire de cocktails."},
        400: {"description": "Nombre invalide (1-5)."},
    },
)
def cocktails_aleatoires(
    nb: Number,
    utilisateur: Optional[Utilisateur] = Depends(obtenir_utilisateur_optionnel),
):
    """
    **Obtenir une sélection aléatoire de cocktails**

    ### Paramètres
    - **nb** *Literal* : Nombre de cocktails à tirer aléatoirement (entre 1 et 5).

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
            est_majeur=est_majeur, nb=int(nb), langue=langue
        )

        id_cocktails = [cocktail.id_cocktail for cocktail in cocktails]

        # Récupérer les ingrédients en une seule requête
        ingredients_par_cocktail = service_cocktail.obtenir_ingredients_par_cocktails(id_cocktails)

        # Construire la réponse avec les ingrédients
        resultats = []
        for cocktail in cocktails:
            cocktail_dict = cocktail.__dict__
            # Ajouter les ingrédients au résultat
            cocktail_dict["ingredients"] = ingredients_par_cocktail.get(cocktail.id_cocktail, [])
            resultats.append(cocktail_dict)

        return {
            "resultats": resultats,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
