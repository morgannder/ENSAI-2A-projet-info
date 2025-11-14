# ENSAI 2A Projet Info - Groupe 10

Tuteur : Elwenn Joubrel

Membres : Isabelle KANTOUSSAN, Sérine OUARAS, Morgann DERICK, Antoine FOUCART

À Portée De Verre : gestion de bar personnel et suggestion de cocktails


# Présentation et description du Projet

Ce projet propose une application pratique et ludique pour la préparation de cocktails.

Les utilisateurs peuvent découvrir les recettes qu'ils peuvent réaliser avec les ingrédients dont ils disposent, ou celles pour lesquelles il ne manque que quelques éléments.

Le projet repose sur une API REST utilisant les données de [TheCocktailDB](https://www.thecocktaildb.com/), fournissant plusieurs informations de centaines de cocktails.

Les utilisateurs peuvent rechercher des recettes, filtrer les résultats et, s’ils sont authentifiés, gérer leur stock d’ingrédients pour obtenir :
- les cocktails réalisables immédiatement
- les cocktails proches, nécessitant peu d’ingrédients supplémentaires

De plus, ils peuvent laisser des commentaires sur les cocktails souhaités et consulter les avis d’autres utilisateurs.



## Outils utilisés

- [Visual Studio Code](https://code.visualstudio.com/)
- [Python 3.13](https://www.python.org/)
- [Git](https://git-scm.com/)
- Une base de données [PostgreSQL](https://www.postgresql.org/)
- [FastAPI](https://fastapi.tiangolo.com/) (Pour notre webservice)


### Connexion DB & Webservice
- [ ] Ouvrir VS_Code avec port 5432 ouvert (via network access)
- [ ] Installer les packages nécessaires via l'environnement virtuelle :
```bash
pip install -r requirements.txt
pip list
```
- [ ] Créer et remplir un fichier .env de la sorte avec les données fournies par POSTGRES:

        POSTGRES_HOST=
        POSTGRES_PORT=
        POSTGRES_USER=
        POSTGRES_DATABASE=defaultdb
        POSTGRES_PASSWORD=
        POSTGRES_SCHEMA=public

        SECRET_KEY =
        ACCESS_TOKEN_EXPIRE_MINUTES =
        ALGORITHM =




## Descriptions de l'arborescence du projet

###  Structure des dossiers

| Dossier | Description |
|---------|-------------|
| **`data/`** | Base de données et fichiers de données persistantes |
| **`doc/`** | Fichiers liés à la gestion du groupe (suivis aux fils des semaines) ainsi qu'aux détails superficielles de notre application (diagrammes, idées de fonctionnalités) |
| **`extractAPI/`** | Scripts d'extraction et d'import de données |
| **`logs/`** | Contient les logs des activités de l'utilisateur |


### Code Source - `src/`

| Dossier | Description |
|---------|-------------|
| **`src/app/`** | Application principale FastAPI qui regroupe tous les endpoints et fonctions internes|
| **`src/app/api/endpoints/`** | Routes et contrôleurs de l'API REST |
| **`src/app/core/`** | Configurations et services essentiels au bon foncitonnement de l'application|
| **`src/app/business_object/`** | Objets métier et entités du domaine (Utilisateur/Inventaire/Cocktail) |
| **`src/app/dao/`** | Data Access Objects (DAO) |
| **`src/app/service/`** | Services et logique applicative |
| **`src/app/tests/`** | Tests unitaires et d'intégration (services et DAO)|
| **`src/app/utils/`** | Fonctions annexes et utilities |






## Lancement du webservice

L'application principal se lance via le main

- [ ] `python main.py`
