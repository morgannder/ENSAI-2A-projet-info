import logging

from business_object.cocktail import Cocktail
from business_object.cocktail_complet import CocktailComplet
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class CocktailDao(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Cocktails de la base de données."""

    # --------------------------  Méthode realiser_cocktail   ---------------------------------

    @log
    def realiser_cocktail(
        self, id_cocktail: int = None, nom_cocktail: str = None, langue: str = "ENG"
    ) -> CocktailComplet:
        """Récupérer les détails complets d'un cocktail par son ID ou son nom.

        Parameters
        ----------
        id_cocktail : int, optional
            Identifiant du cocktail.
        nom_cocktail : str, optional
            Nom du cocktail (insensible à la casse).
        langue : str
            Langue des instructions.

        Returns
        -------
        Cocktail
            Le cocktail trouvé avec toutes ses informations.

        Raises
        ------
        ValueError
            Si aucun identifiant n'est fourni ou si le cocktail n'existe pas.
        """
        if id_cocktail is None and not nom_cocktail:
            raise ValueError("Vous devez fournir soit un ID, soit un nom de cocktail")

        col_instructions = self.instruction_column(langue)

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    where_clause = ""
                    params = {}

                    if id_cocktail is not None:
                        where_clause = "WHERE c.id_cocktail = %(id_cocktail)s"
                        params["id_cocktail"] = id_cocktail
                    else:
                        where_clause = "WHERE LOWER(c.nom_cocktail) = LOWER(%(nom_cocktail)s)"
                        params["nom_cocktail"] = nom_cocktail

                    cursor.execute(
                        f"""
                            SELECT
                                c.id_cocktail,
                                c.nom_cocktail,
                                c.categorie,
                                c.alcool,
                                c.image_url,
                                c.verre,
                                c.{col_instructions} AS instructions,
                                STRING_AGG(i.nom_ingredient, '|||' ORDER BY i.nom_ingredient) AS ingredients,
                                STRING_AGG(COALESCE(ci.quantite, 'NULL'), '|||' ORDER BY i.nom_ingredient) AS quantites
                            FROM cocktail c
                            JOIN cocktail_ingredient ci ON c.id_cocktail = ci.id_cocktail
                            JOIN ingredient i ON ci.id_ingredient = i.id_ingredient
                            {where_clause}
                            GROUP BY
                                c.id_cocktail, c.nom_cocktail, c.categorie,
                                c.alcool, c.image_url, c.verre, c.{col_instructions}
                            """,
                        params,
                    )

                    # On ne renvoi qu'un seul
                    row = cursor.fetchone()

                    if not row:
                        return None

                    cocktail = CocktailComplet(
                        id_cocktail=row["id_cocktail"],
                        nom_cocktail=row["nom_cocktail"],
                        categ_cocktail=row["categorie"],
                        image_cocktail=row.get("image_url"),
                        alcoolise_cocktail=row.get("alcool"),
                        instruc_cocktail=row.get("instructions"),
                        verre=row.get("verre"),
                        ingredients=row.get("ingredients"),
                        quantites=row.get("quantites"),
                    )

                    return cocktail

        except Exception:
            logging.exception("Erreur lors dde la récupération du cocktail")
            raise

    # --------------------------  Méthode cocktail_partiel   ---------------------------------

    @log
    def cocktail_complet(
        self, id_utilisateur: int, langue: str = "ENG", limite: int = 10, decalage: int = 0
    ) -> list[Cocktail]:
        """Lister tous les cocktails que l'utilisateur peut préparer à partir de son inventaire.

        Parameters
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur.
        langue : str
            Langue de l'utilisateur.
        limite : int, optional
            Nombre maximal de résultats retournés (pagination). Par défaut 10.
        decalage : int, optional
            Décalage pour la pagination. Par défaut 0.

        Returns
        -------
        list[Cocktail]
            Liste des cocktails préparables avec l'inventaire complet.
        """

        # --- Choix de la colonne instructions selon la langue ---
        col_instructions = self.instruction_column(langue)

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # Requête unique utilisant des CTE (Pour réduire le nombre d'aller-retour DB ):
                    # 1) user_ingredients : ingrédients de l'utilisateur
                    # 2) cocktail_ingredient_count : nombre d'ingrédients requis par cocktail
                    # 3) cocktail_matching_ingredients : nombre d'ingrédients disponibles pour chaque cocktail dans l'inventaire
                    # On sélectionne les cocktails dont total_ingredients == matching_ingredients
                    cursor.execute(
                        f"""
                        WITH user_ingredients AS (
                            SELECT id_ingredient
                            FROM inventaire_ingredient
                            WHERE id_utilisateur = %(id_utilisateur)s
                        ),
                        cocktail_ingredient_count AS (
                            SELECT id_cocktail, COUNT(*) AS total_ingredients
                            FROM cocktail_ingredient
                            GROUP BY id_cocktail
                        ),
                        cocktail_matching_ingredients AS (
                            SELECT ci.id_cocktail, COUNT(*) AS matching_ingredients
                            FROM cocktail_ingredient ci
                            JOIN user_ingredients ui ON ci.id_ingredient = ui.id_ingredient
                            GROUP BY ci.id_cocktail
                        )
                        SELECT c.id_cocktail, c.nom_cocktail, c.categorie, c.alcool, c.image_url, c.verre, c.{col_instructions} AS instructions
                        FROM cocktail c
                        JOIN cocktail_ingredient_count cic ON c.id_cocktail = cic.id_cocktail
                        JOIN cocktail_matching_ingredients cmi ON c.id_cocktail = cmi.id_cocktail
                        WHERE cic.total_ingredients = cmi.matching_ingredients
                        ORDER BY c.nom_cocktail
                        LIMIT %(limite)s OFFSET %(decalage)s;
                        """,
                        {
                            "id_utilisateur": id_utilisateur,
                            "limite": limite,
                            "decalage": decalage,
                        },
                    )
                    rows = cursor.fetchall()

                    return [
                        Cocktail(
                            id_cocktail=row["id_cocktail"],
                            nom_cocktail=row["nom_cocktail"],
                            categ_cocktail=row["categorie"],
                            image_cocktail=row.get("image_url"),
                            alcoolise_cocktail=row.get("alcool"),
                            instruc_cocktail=row.get("instructions"),
                            verre=row.get("verre"),
                        )
                        for row in rows
                    ]

        except Exception:
            logging.exception("Erreur cocktail_complet pour user %s", id_utilisateur)
            raise

    # -------------------------- Méthode: cocktail_partiel -----------------------------

    @log
    def cocktail_partiel(
        self,
        id_utilisateur: int,
        nb_manquants: int,
        langue: str = "ENG",
        limite: int = 10,
        decalage: int = 0,
    ) -> list[Cocktail]:
        """Lister tous les cocktails préparables avec au plus nb_manquants ingrédients manquants.

        Parameters
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur.
        nb_manquants : int
            Nombre maximal d'ingrédients manquants autorisés.
        langue : str
            Langue de l'utilisateur.
        limite : int, optional
            Pagination — nombre maximum de résultats.
        decalage : int, optional
            décalage des résultats.

        Returns
        -------
        list[Cocktail]
            Liste des cocktails partiellement préparables avec l'inventaire.
        """

        # --- Choix de la colonne instructions selon la langue ---
        col_instructions = self.instruction_column(langue)

        # On limite le nombre d'ingrédients manquants pour éviter des résultats trop larges et peu pertinents.
        nb_manquants = min(nb_manquants, 5)

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # Requête unique utilisant des CTE (même principe que la première) :
                    # 1) cocktail_ingredient_count : nombre total d'ingrédients requis pour chaque cocktail
                    # 2) cocktail_matching_ingredients : nombre d'ingrédients déjà présents dans l'inventaire de l'utilisateur (LEFT JOIN )
                    # ex: Mojito 5 ingrédients, utilisateur n'a que "eau" -> avec INNER JOIN il disparaît, LEFT JOIN permet de le garder
                    # 3) Sélection finale : cocktails avec <= nb_manquants ingrédients manquants, triés par nombre d'ingrédients manquants puis par nom, avec pagination LIMIT/OFFSET

                    cursor.execute(
                        f"""
                        WITH cocktail_ingredient_count AS (
                            SELECT id_cocktail, COUNT(*) AS total_ingredients
                            FROM cocktail_ingredient
                            GROUP BY id_cocktail
                        ),
                        cocktail_matching_ingredients AS (
                            SELECT c.id_cocktail, COUNT(ui.id_ingredient) AS matching_ingredients
                            FROM cocktail c
                            LEFT JOIN cocktail_ingredient ci ON c.id_cocktail = ci.id_cocktail
                            LEFT JOIN inventaire_ingredient ui
                                ON ci.id_ingredient = ui.id_ingredient
                                AND ui.id_utilisateur = %(id_utilisateur)s
                            GROUP BY c.id_cocktail
                        )
                        SELECT c.id_cocktail, c.nom_cocktail, c.categorie, c.alcool, c.image_url, c.verre, c.{col_instructions} AS instructions, cic.total_ingredients, cmi.matching_ingredients
                        FROM cocktail c
                        JOIN cocktail_ingredient_count cic ON c.id_cocktail = cic.id_cocktail
                        JOIN cocktail_matching_ingredients cmi ON c.id_cocktail = cmi.id_cocktail
                        WHERE (cic.total_ingredients - cmi.matching_ingredients) <= %(nb_manquants)s
                        AND (cic.total_ingredients - cmi.matching_ingredients) >= 1
                        ORDER BY
                            (cic.total_ingredients - cmi.matching_ingredients) ASC,
                            c.nom_cocktail
                        LIMIT %(limite)s OFFSET %(decalage)s;
                        """,
                        {
                            "id_utilisateur": id_utilisateur,
                            "nb_manquants": nb_manquants,
                            "limite": limite,
                            "decalage": decalage,
                        },
                    )
                    rows = cursor.fetchall()

                    return [
                        Cocktail(
                            id_cocktail=row["id_cocktail"],
                            nom_cocktail=row["nom_cocktail"],
                            categ_cocktail=row["categorie"],
                            image_cocktail=row.get("image_url"),
                            alcoolise_cocktail=row.get("alcool"),
                            instruc_cocktail=row.get("instructions"),
                            verre=row.get("verre"),
                        )
                        for row in rows
                    ]
        except Exception:
            logging.exception("Erreur cocktail_partiel pour user %s", id_utilisateur)
            raise

    # ------------------------  Méthode: rechercher_cocktails -----------------------------

    @log
    def rechercher_cocktails(
        self,
        nom_cocktail=None,
        categorie=None,
        verre=None,
        alcool=None,
        ingredients=None,
        langue: str = "ENG",
        limite: int = 10,
        decalage: int = 0,
    ) -> list[Cocktail]:
        """Recherche de cocktails avec filtres et pagination (VERSION OPTIMALE).

        Parameters
        ----------
        nom_cocktail : str, optional
            Filtre sur le nom du cocktail (insensible à la casse).
        categorie : str, optional
            Filtre sur la catégorie du cocktail.
        verre : str, optional
            Filtre sur le type de verre.
        alcool : str, optional
            Filtre sur le type d'alcool.
        ingredients : list[str], optional
            Liste d'ingrédients (le cocktail doit contenir TOUS ces ingrédients).
        langue : str
            Langue de l'utilisateur.
        limite : int, optional
            Nombre maximal de cocktails retournés
        decalage : int, optional
            Décalage du résultat pour la pagination

        Returns
        -------
        list[Cocktail]
            Liste des cocktails correspondant aux filtres appliqués.
        """

        # --- Choix de la colonne instructions selon la langue ---
        col_instructions = self.instruction_column(langue)

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    params = {"limite": limite, "decalage": decalage}
                    # Mapping entre la langue saisi de l'utilisateur et la bonne colonne

                    # On utilise une CTE pour filtrer par ingrédients si nécessaire
                    if ingredients and len(ingredients) > 0:
                        # CTE pour trouver les cocktails qui ont TOUS les ingrédients demandés
                        query = f"""
                            WITH cocktails_with_ingredients AS (
                                SELECT c.id_cocktail
                                FROM cocktail c
                                JOIN cocktail_ingredient ci ON c.id_cocktail = ci.id_cocktail
                                JOIN ingredient i ON ci.id_ingredient = i.id_ingredient
                                WHERE LOWER(i.nom_ingredient) = ANY(%(ingredients)s)
                                GROUP BY c.id_cocktail
                                HAVING COUNT(DISTINCT i.id_ingredient) = %(nb_ingredients)s
                            )
                            SELECT c.id_cocktail, c.nom_cocktail, c.categorie, c.alcool, c.image_url, c.verre, c.{col_instructions} AS instructions
                            FROM cocktail c
                            JOIN cocktails_with_ingredients cwi ON c.id_cocktail = cwi.id_cocktail
                            WHERE 1=1
                        """
                        # Normaliser les noms d'ingrédients en lowercase pour éviter les problèmes de casse
                        params["ingredients"] = [ing.lower() for ing in ingredients]
                        params["nb_ingredients"] = len(ingredients)
                    else:
                        # Pas de filtre d'ingrédients, requête simple
                        query = f"""
                        SELECT c.id_cocktail, c.nom_cocktail, c.categorie, c.alcool, c.image_url, c.verre, c.{col_instructions} AS instructions
                        FROM cocktail c WHERE 1=1
                        """

                    if nom_cocktail is not None:
                        query += " AND nom_cocktail ILIKE %(nom_cocktail)s"
                        params["nom_cocktail"] = f"%{nom_cocktail}%"

                    if categorie is not None:
                        query += " AND LOWER(categorie) = LOWER(%(categorie)s)"
                        params["categorie"] = categorie.lower()

                    if verre is not None:
                        query += " AND LOWER(verre) = LOWER(%(verre)s)"
                        params["verre"] = verre.lower()

                    if alcool is not None:
                        query += " AND LOWER(alcool)= LOWER( %(alcool)s)"
                        params["alcool"] = alcool.lower()

                    # Tri et pagination
                    query += " ORDER BY nom_cocktail LIMIT %(limite)s OFFSET %(decalage)s;"

                    cursor.execute(query, params)
                    rows = cursor.fetchall()

                    return [
                        Cocktail(
                            id_cocktail=row["id_cocktail"],
                            nom_cocktail=row["nom_cocktail"],
                            categ_cocktail=row["categorie"],
                            image_cocktail=row.get("image_url"),
                            alcoolise_cocktail=row.get("alcool"),
                            instruc_cocktail=row.get("instructions"),
                            verre=row.get("verre"),
                        )
                        for row in rows
                    ]
        except Exception:
            logging.exception("Erreur rechercher_cocktails")
            raise

    # ------------------- Méthode: cocktails_aleatoires -----------------------------

    @log
    def cocktails_aleatoires(
        self,
        nombre: int = 5,
        langue: str = "ENG",
    ) -> list[Cocktail]:
        """Propose une liste de cocktails choisis aléatoirement.

        Parameters
        ----------
        nombre : int, optional
            Nombre de cocktails à sélectionner (par défaut 5)
        langue : str
            Langue de l'utilisateur.

        Returns
        -------
        list[Cocktail]
            Liste de cocktails aléatoires sélectionnés directement côté base de données.

        """
        # --- Choix de la colonne instructions selon la langue ---
        col_instructions = self.instruction_column(langue)

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    nombre_limite = min(max(1, nombre), 5)

                    cursor.execute(
                        f"""SELECT id_cocktail, nom_cocktail, categorie, alcool, image_url, verre, {col_instructions} AS instructions
                        FROM cocktail
                        ORDER BY RANDOM()
                        LIMIT %(limite)s;""",
                        {"limite": nombre_limite},
                    )
                    rows = cursor.fetchall()

                    return [
                        Cocktail(
                            id_cocktail=row["id_cocktail"],
                            nom_cocktail=row["nom_cocktail"],
                            categ_cocktail=row["categorie"],
                            image_cocktail=row.get("image_url"),
                            alcoolise_cocktail=row.get("alcool"),
                            instruc_cocktail=row.get("instructions"),
                            verre=row.get("verre"),
                        )
                        for row in rows
                    ]
        except Exception:
            logging.exception("Erreur cocktails_aleatoires")
            raise

    # ------------------- Méthode: instruction_column -----------------------------

    def instruction_column(self, langue: str) -> str:
        """
        Retourne le nom de la colonne SQL contenant les instructions
        du cocktail, en fonction de la langue préférée de l'utilisateur.

        Parameters
        ----------
        langue : str
            Code de la langue (ex: "ENG", "FRA", "ESP", "GER", "ITA").

        Returns
        -------
        str
            Nom de la colonne instructions correspondant à la langue.
            Par défaut, renvoie "instructions" (anglais).
        """
        # En base de données, chaque cocktail a plusieurs colonnes pour les instructions
        # : instructions (anglais), instructions_fr, instructions_es, instructions_de, instructions_it.
        # Cela permet de récupérer directement la bonne colonne selon la langue de l'utilisateur
        langue_map = {
            "ENG": "instructions",
            "FRA": "instructions_fr",
            "ESP": "instructions_es",
            "GER": "instructions_de",
            "ITA": "instructions_it",
            "string": "instructions",  # Fallback par défaut
        }
        return langue_map.get(langue.upper(), "instructions")

        # ------------------- Méthode: trouver_par_id -----------------------------

    @log
    def trouver_par_id(self, id_cocktail: int) -> Cocktail:
        """
        Trouver un cocktail par son ID.

        Parameters
        ----------
        id_cocktail : int
            ID du cocktail recherché

        Returns
        -------
        Cocktail
            Le cocktail trouvé ou None
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM cocktail WHERE id_cocktail = %(id_cocktail)s;",
                        {"id_cocktail": id_cocktail},
                    )
                    row = cursor.fetchone()
                    if row:
                        return Cocktail(
                            id_cocktail=row["id_cocktail"],
                            nom_cocktail=row["nom_cocktail"],
                            categ_cocktail=row["categorie"],
                            image_cocktail=row.get("image_url"),
                            alcoolise_cocktail=row.get("alcool"),
                            instruc_cocktail=row.get("instructions"),
                        )
                    return None
        except Exception as e:
            print(f"Erreur recherche cocktail par ID: {e}")

        # ------------------- Méthode: trouver_les_ingrédients -----------------------------

    @log
    def obtenir_ingredients_par_cocktails(self, id_cocktails: list[int]) -> dict[int, list[str]]:
        """
        Récupère tous les ingrédients pour une liste de cocktails

        Parameters
        ----------
        id_cocktails : list[int]
            ID des cocktails recherchés

        Returns
        -------
        dict { int : list[str] }
            Dictionnaire avec la liste des ingrédients nécessaire pour chaque cocktails
        """
        if not id_cocktails:
            return {}

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT
                            ci.id_cocktail,
                            STRING_AGG(i.nom_ingredient, '|||' ORDER BY i.nom_ingredient) AS ingredients
                        FROM cocktail_ingredient ci
                        JOIN ingredient i ON ci.id_ingredient = i.id_ingredient
                        WHERE ci.id_cocktail = ANY(%(id_cocktails)s)
                        GROUP BY ci.id_cocktail
                    """,
                        {"id_cocktails": id_cocktails},
                    )

                    rows = cursor.fetchall()

                    # Créer un dictionnaire {id_cocktail: [ingrédients]}
                    return {row["id_cocktail"]: row["ingredients"].split("|||") for row in rows}
        except Exception:
            logging.exception("Erreur get_ingredients_par_cocktails")
            return {}

    @log
    def obtenir_ingredients_possedes_par_cocktails(
        self, id_utilisateur: int, id_cocktails: list[int]
    ) -> dict[int, list[str]]:
        """
        Récupère les ingrédients possédés par l'utilisateur
        pour chaque cocktail d'une liste de cocktails

        Parameters
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur
        id_cocktails : list[int]
            ID des cocktails recherchés

        Returns
        -------
        dict { int : list[str] }
            Dictionnaire avec la liste des ingrédients nécessaire pour chaque cocktails
        """
        if not id_cocktails:
            return {}

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT
                            ci.id_cocktail,
                            STRING_AGG(i.nom_ingredient, '|||' ORDER BY i.nom_ingredient) AS ingredients_possedes
                        FROM cocktail_ingredient ci
                        JOIN ingredient i ON ci.id_ingredient = i.id_ingredient
                        JOIN inventaire_ingredient inv ON i.id_ingredient = inv.id_ingredient
                        WHERE ci.id_cocktail = ANY(%(id_cocktails)s)
                        AND inv.id_utilisateur = %(id_utilisateur)s
                        GROUP BY ci.id_cocktail
                    """,
                        {"id_cocktails": id_cocktails, "id_utilisateur": id_utilisateur},
                    )

                    rows = cursor.fetchall()

                    # Créer un dictionnaire {id_cocktail: [ingrédients_possedes]}
                    return {
                        row["id_cocktail"]: row["ingredients_possedes"].split("|||") for row in rows
                    }
        except Exception:
            logging.exception("Erreur obtenir_ingredients_possedes_par_cocktails")
            return {}
