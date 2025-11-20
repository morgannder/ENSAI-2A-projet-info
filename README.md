# ENSAI 2A Information Project - Group 10

Tutor: Elwenn Joubrel

Members: Isabelle KANTOUSSAN, Sérine OUARAS, Morgann DERICK, Antoine FOUCART

À Portée De Verre: personal bar management and cocktail suggestion tool


# Project Overview and Description

This project provides a practical and entertaining application for cocktail preparation.

Users can explore recipes they can make with the ingredients they already have, or recipes for which they only need a few additional elements.

The project is based on a REST API using data from [TheCocktailDB](https://www.thecocktaildb.com/), providing information on hundreds of cocktails.

Users can search for recipes, filter results, and—if authenticated—manage their ingredient inventory to obtain:
- cocktails they can make immediately
- cocktails that are close to being achievable, requiring only a few extra ingredients

Additionally, they can leave comments on cocktails and view reviews from other users.


## Tools Used

- [Visual Studio Code](https://code.visualstudio.com/)
- [Python 3.13](https://www.python.org/)
- [Git](https://git-scm.com/)
- A [PostgreSQL](https://www.postgresql.org/) database
- [FastAPI](https://fastapi.tiangolo.com/) (for our web service)


### DB Connection & Webservice Setup

- [ ] Open VS Code with port 5432 accessible (via network access)
- [ ] Install the required packages using the virtual environment:

```bash
pip install -r requirements.txt
pip list
```
- [ ] Create and fill a .env file like the following, using the PostgreSQL credentials provided:

        POSTGRES_HOST=
        POSTGRES_PORT=
        POSTGRES_USER=
        POSTGRES_DATABASE=defaultdb
        POSTGRES_PASSWORD=
        POSTGRES_SCHEMA=public

        SECRET_KEY =
        ACCESS_TOKEN_EXPIRE_MINUTES =
        ALGORITHM =




## Project Directory Structure

###  Folder Structure

| Folder | Description |
|---------|-------------|
| **`data/`** | Database and persistent data files |
| **`doc/`** | Files related to group management (weekly progress) and non-essential application details (diagrams, feature ideas) |
| **`extractAPI/`** | Scripts for data extraction and import |
| **`logs/`** | Contains logs of user activity |


### Source Code - `src/`

| Folder | Description |
|---------|-------------|
| **`src/app/`** | Main FastAPI application containing all endpoints and internal functions|
| **`src/app/api/endpoints/`** | Routes and controllers for the REST API |
| **`src/app/core/`** | Core configurations and essential services for the application|
| **`src/app/business_object/`** | Business objects and domain entities (User / Inventory / Cocktail) |
| **`src/app/dao/`** | Data Access Objects (DAO) |
| **`src/app/service/`** | Services and application logic |
| **`src/app/tests/`** | Unit and integration tests (services & DAO)|
| **`src/app/utils/`** | Utility and helper functions |






## Running the Webservice

The main application is launched via:

- [ ] `python main.py`
