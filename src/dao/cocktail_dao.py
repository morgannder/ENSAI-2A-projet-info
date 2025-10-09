import logging

from business_object.cocktail import Cocktail
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class CocktailDao(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Cocktails de la base de données"""

    @log
    def rechercher_cocktail_par_mon(self, nom_cocktail) -> list[Cocktail]:
        """trouver un cocktail grace à son nom

        Parameters
        ----------
        nom_cocktail : str
            nom du coktail que l'on souhaite trouver

        Returns
        -------
        liste_cocktails : list[Cocktails]
            renvoie la liste des cocktails comportant le nom
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                           "
                        "  FROM cocktail                    "
                        " WHERE nom_cocktail LIKE %(nom_cocktail)s;  ",
                        {"nom_cocktail": f"%{nom_cocktail}%"},
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        liste_cocktails = []
        if res:
            for row in res:
                liste_cocktails.append(
                    Cocktail(
                        id_cocktail=row["id_cocktail"],
                        nom_cocktail=row["nom_cocktail"],
                        categ_cocktail=row["categ_cocktail"],
                        image_cocktail=row["image_cocktail"],
                        alcoolise_cocktail=row["alcoolise_cocktail"],
                        instruc_cocktail=row["instruc_cocktail"],
                    )
                )

        return liste_cocktails

    @log
    def cocktail_complet(self, id_utilisateur: int) -> list[Cocktail]:
        """Lister tous les cocktails que l'utilisateur peut préparer à partir de son inventaire.

        Parameters
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur dont on veut vérifier l'inventaire.

        Returns
        -------
        liste_cocktails : list[Cocktail]
            Renvoie la liste de tous les cocktails que l'utilisateur peut préparer
            avec son inventaire complet d'ingrédients.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:

                    #On recupére tous les cocktails de la bd

                    cursor.execute("""SELECT * FROM cocktail;""")
                    cocktails = cursor.fetchall()

                    #les ingrédients de l'utilisateur qui sont dans son inventaire

                    cursor.execute(
                        """SELECT id_ingredient FROM inventaire_ingredient WHERE id_utilisateur = %(id_utilisateur)s;""",
                        {"id_utilisateur": id_utilisateur}
                    )

                    inventaire = []

                    for i in cursor.fetchall():
                        inventaire.append(i["id_ingredient"])

                    liste_cocktails = []
                    for c in cocktails:
                        cursor.execute(
                            """SELECT id_ingredient FROM cocktail_ingredient WHERE id_cocktail = %(id_cocktail)s;""",
                            {"id_cocktail": c["id_cocktail"]}
                        )

                        ingredients_cocktail = []
                        for row in cursor.fetchall():
                            ingredients_cocktail.append(row["id_ingredient"])

                        # Vérifier que l'utilisateur a tous les ingrédients
                        if set(ingredients_cocktail).issubset(set(inventaire)):
                            liste_cocktails.append(
                                Cocktail(
                                    id_cocktail=c["id_cocktail"],
                                    nom_cocktail=c["nom_cocktail"],
                                    categ_cocktail=c["categorie"],
                                    image_cocktail=c["image_url"],
                                    alcoolise_cocktail=c["alcool"],
                                    instruc_cocktail=c["instructions"],
                                )
                            )
        except Exception as e:
            logging.info(e)
            raise

        return liste_cocktails


    @log
    def cocktail_partiel(self, id_utilisateur: int, nb_manquants: int) -> list[Cocktail]:
        """Lister tous les cocktails que l'utilisateur peut préparer avec au plus n ingrédients manquants.

        Parameters
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur dont on veut vérifier l'inventaire.
        nb_manquants : int
            Nombre maximal d'ingrédients manquants autorisés pour préparer un cocktail.

        Returns
        -------
        liste_cocktails : list[Cocktail]
            Renvoie la liste des cocktails que l'utilisateur peut préparer
            en ayant au plus nb_manquants ingrédients manquants.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:

                    #On recupére tous les cocktails de la bd

                    cursor.execute("""SELECT * FROM cocktail;""")
                    cocktails = cursor.fetchall()

                    #On recupére les ingrédients de l'utilisateur qui sont dans son inventaire

                    cursor.execute(
                        """SELECT id_ingredient FROM inventaire_ingredient WHERE id_utilisateur = %(id_utilisateur)s;""",
                        {"id_utilisateur": id_utilisateur}
                    )

                    inventaire = []
                    for i in cursor.fetchall():
                        inventaire.append(i["id_ingredient"])

                    liste_cocktails = []
                    for c in cocktails:

                        #Les ingrédients nécessaires pour ce cocktail

                        cursor.execute(
                            """SELECT id_ingredient FROM cocktail_ingredient WHERE id_cocktail = %(id_cocktail)s;""",
                            {"id_cocktail": c["id_cocktail"]}
                        )

                        ingredients_cocktail = []
                        for row in cursor.fetchall():
                            ingredients_cocktail.append(row["id_ingredient"])

                        #Vérifier combien d'ingrédients manquent
                        manquants = set(ingredients_cocktail) - set(inventaire)

                        # Si le nombre d'ingrédients manquants est inférieur ou égal à nb_manquants, on garde le cocktail

                        if len(manquants) <= nb_manquants:
                            liste_cocktails.append(
                                Cocktail(
                                    id_cocktail=c["id_cocktail"],
                                    nom_cocktail=c["nom_cocktail"],
                                    categ_cocktail=c["categorie"],
                                    image_cocktail=c["image_url"],
                                    alcoolise_cocktail=c["alcool"],
                                    instruc_cocktail=c["instructions"],
                                )
                            )

        except Exception as e:
            logging.info(e)
            raise

        return liste_cocktails


    @log
    def rechercher_cocktails(self,nom_cocktail =None, categorie =None, verre =None) -> list[Cocktail]:
        """Recherche de cocktails avec plusieurs filtres optionnels.

        Parameters
        ----------
        nom_cocktail : str, optional
            Nom du cocktail à rechercher (partie du nom).
        categorie : str, optional
            Filtrer par catégorie.
        verre : str, optional
            Filtrer par type de verre.

        Returns
        -------
        liste_cocktails : list[Cocktail]
            Liste des cocktails correspondant aux filtres donnés.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:

                    # On commence par sélectionner tous les cocktails
                    query = """SELECT * FROM cocktail WHERE 1=1"""
                    params = {}

                    # -----------------Filtrage par nom ---------------
                    if nom_cocktail is not None:
                        query += " AND nom_cocktail ILIKE %(nom_cocktail)s"
                        params["nom_cocktail"] = f"%{nom_cocktail}%"

                    # -----------------Filtrage par catégorie ---------
                    if categorie is not None:
                        query += " AND categorie = %(categorie)s"
                        params["categorie"] = categorie

                    # ------------------Filtrage par type de verre-----
                    if verre is not None:
                        query += " AND verre = %(verre)s"
                        params["verre"] = verre

                    #Execution de la requête
                    cursor.execute(query, params)
                    cocktails = cursor.fetchall()

                    #liste finale des objets Cocktail
                    liste_cocktails = []
                    for c in cocktails:
                        liste_cocktails.append(
                            Cocktail(
                                id_cocktail=c["id_cocktail"],
                                nom_cocktail=c["nom_cocktail"],
                                categ_cocktail=c["categorie"],
                                image_cocktail=c["image_url"],
                                alcoolise_cocktail=c["alcool"],
                                instruc_cocktail=c["instructions"],
                            )
                        )

        except Exception as e:
            logging.info(e)
            raise

        return liste_cocktails
