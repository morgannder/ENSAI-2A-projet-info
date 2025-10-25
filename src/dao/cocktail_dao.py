import logging

from business_object.cocktail import Cocktail
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class CocktailDao(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Cocktails de la base de données."""

    # --------------------------  Méthode cocktail_partiel   ---------------------------------

    @log
    def cocktail_complet(
        self, id_utilisateur: int, limit: int = 10, offset: int = 0
    ) -> list[Cocktail]:
        """Lister tous les cocktails que l'utilisateur peut préparer à partir de son inventaire.

        Parameters
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur.
        limit : int, optional
            Nombre maximal de résultats retournés (pagination). Par défaut 10.
        offset : int, optional
            Décalage pour la pagination. Par défaut 0.

        Returns
        -------
        list[Cocktail]
            Liste des cocktails préparables avec l'inventaire complet.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # Requête unique utilisant des CTE (Pour réduire le nombre d'aller-retour DB ):
                    # 1) user_ingredients : ingrédients de l'utilisateur
                    # 2) cocktail_ingredient_count : nombre d'ingrédients requis par cocktail
                    # 3) cocktail_matching_ingredients : nombre d'ingrédients disponibles pour chaque cocktail dans l'inventaire
                    # On sélectionne les cocktails dont total_ingredients == matching_ingredients
                    cursor.execute(
                        """
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
                        SELECT c.*
                        FROM cocktail c
                        JOIN cocktail_ingredient_count cic ON c.id_cocktail = cic.id_cocktail
                        JOIN cocktail_matching_ingredients cmi ON c.id_cocktail = cmi.id_cocktail
                        WHERE cic.total_ingredients = cmi.matching_ingredients
                        ORDER BY c.nom_cocktail
                        LIMIT %(limit)s OFFSET %(offset)s;
                        """,
                        {"id_utilisateur": id_utilisateur, "limit": limit, "offset": offset},
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
                        )
                        for row in rows
                    ]

        except Exception:
            logging.exception("Erreur cocktail_complet pour user %s", id_utilisateur)
            raise

    # -------------------------- Méthode: cocktail_partiel -----------------------------

    @log
    def cocktail_partiel(
        self, id_utilisateur: int, nb_manquants: int, limit: int = 10, offset: int = 0
    ) -> list[Cocktail]:
        """Lister tous les cocktails préparables avec au plus nb_manquants ingrédients manquants.

        Parameters
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur.
        nb_manquants : int
            Nombre maximal d'ingrédients manquants autorisés.
        limit : int, optional
            Pagination — nombre maximum de résultats.
        offset : int, optional
            décalage des résultats.
        """

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
                        """
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
                        SELECT c.*, cic.total_ingredients, cmi.matching_ingredients
                        FROM cocktail c
                        JOIN cocktail_ingredient_count cic ON c.id_cocktail = cic.id_cocktail
                        JOIN cocktail_matching_ingredients cmi ON c.id_cocktail = cmi.id_cocktail
                        WHERE (cic.total_ingredients - cmi.matching_ingredients) <= %(nb_manquants)s
                        ORDER BY
                            (cic.total_ingredients - cmi.matching_ingredients) ASC,
                            c.nom_cocktail
                        LIMIT %(limit)s OFFSET %(offset)s;
                        """,
                        {
                            "id_utilisateur": id_utilisateur,
                            "nb_manquants": nb_manquants,
                            "limit": limit,
                            "offset": offset,
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
        limit: int = 10,
        offset: int = 0,
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
        limit : int, optional
            Nombre maximal de cocktails retournés
        offset : int, optional
            Décalage du résultat pour la pagination

        Returns
        -------
        list[Cocktail]
            Liste des cocktails correspondant aux filtres appliqués.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    params = {"limit": limit, "offset": offset}

                    # On utilise une CTE pour filtrer par ingrédients si nécessaire
                    if ingredients and len(ingredients) > 0:
                        # CTE pour trouver les cocktails qui ont TOUS les ingrédients demandés
                        query = """
                            WITH cocktails_with_ingredients AS (
                                SELECT c.id_cocktail
                                FROM cocktail c
                                JOIN cocktail_ingredient ci ON c.id_cocktail = ci.id_cocktail
                                JOIN ingredient i ON ci.id_ingredient = i.id_ingredient
                                WHERE LOWER(i.nom_ingredient) = ANY(%(ingredients)s)
                                GROUP BY c.id_cocktail
                                HAVING COUNT(DISTINCT i.id_ingredient) = %(nb_ingredients)s
                            )
                            SELECT c.*
                            FROM cocktail c
                            JOIN cocktails_with_ingredients cwi ON c.id_cocktail = cwi.id_cocktail
                            WHERE 1=1
                        """
                        # Normaliser les noms d'ingrédients en lowercase pour éviter les problèmes de casse
                        params["ingredients"] = [ing.lower() for ing in ingredients]
                        params["nb_ingredients"] = len(ingredients)
                    else:
                        # Pas de filtre d'ingrédients, requête simple
                        query = "SELECT * FROM cocktail WHERE 1=1"

                    if nom_cocktail is not None:
                        query += " AND nom_cocktail ILIKE %(nom_cocktail)s"
                        params["nom_cocktail"] = f"%{nom_cocktail}%"

                    if categorie is not None:
                        query += " AND categorie = %(categorie)s"
                        params["categorie"] = categorie

                    if verre is not None:
                        query += " AND verre = %(verre)s"
                        params["verre"] = verre

                    if alcool is not None:
                        query += " AND alcool = %(alcool)s"
                        params["alcool"] = alcool

                    # Tri et pagination
                    query += " ORDER BY nom_cocktail LIMIT %(limit)s OFFSET %(offset)s;"

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
                        )
                        for row in rows
                    ]
        except Exception:
            logging.exception("Erreur rechercher_cocktails")
            raise

    # ------------------- Méthode: cocktails_aleatoires -----------------------------

    @log
    def cocktails_aleatoires(self, nombre: int = 5) -> list[Cocktail]:
        """Propose une liste de cocktails choisis aléatoirement.

        Parameters
        ----------
        nombre : int, optional
            Nombre de cocktails à sélectionner (par défaut 5)

        Returns
        -------
        list[Cocktail]
            Liste de cocktails aléatoires sélectionnés directement côté base de données.

        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    nombre_limite = min(max(1, nombre), 5)

                    cursor.execute(
                        "SELECT * FROM cocktail ORDER BY RANDOM() LIMIT %(limit)s;",
                        {"limit": nombre_limite},
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
                        )
                        for row in rows
                    ]
        except Exception:
            logging.exception("Erreur cocktails_aleatoires")
            raise

    # ------------------- Méthode: lister_categories -----------------------------

    @log
    def lister_categories(self) -> list[str]:
        """Liste toutes les catégories de cocktails disponibles.

        Returns
        -------
        list[str]
            Liste des catégories uniques, triées alphabétiquement.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT DISTINCT categorie 
                        FROM cocktail 
                        WHERE categorie IS NOT NULL
                        ORDER BY categorie;
                        """
                    )
                    rows = cursor.fetchall()
                    return [row["categorie"] for row in rows]
        except Exception:
            logging.exception("Erreur lister_categories")
            raise

    # ------------------- Méthode: lister_verres -----------------------------

    @log
    def lister_verres(self) -> list[str]:
        """Liste tous les types de verres disponibles.

        Returns
        -------
        list[str]
            Liste des types de verres uniques, triés alphabétiquement.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT DISTINCT verre 
                        FROM cocktail 
                        WHERE verre IS NOT NULL
                        ORDER BY verre;
                        """
                    )
                    rows = cursor.fetchall()
                    return [row["verre"] for row in rows]
        except Exception:
            logging.exception("Erreur lister_verres")
            raise
