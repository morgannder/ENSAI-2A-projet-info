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
                        " WHERE nom LIKE %(nom_cocktail)s;  ",
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
    def cocktail_complet(self) -> list[Cocktail]:
        """Lister tous les cocktails que l'utilisateur peut préparer à partir de son inventaire

        Parameters
        ----------
        None

        Returns
        -------
        liste_cocktails : list[Cocktail]
            Renvoie la liste de tous les cocktails que l'utilisateur peut préparer avec son inventaire
        """

        # try:
        #     with DBConnection().connection as connection:
        #         with connection.cursor() as cursor:
        #             cursor.execute(
        #                 # "SELECT *                              "
        #                 # "  FROM joueur;                        "
        #             )
        #             res = cursor.fetchall()
        # except Exception as e:
        #     logging.info(e)
        #     raise

        # liste_cocktails = []

        # if res:
        #     for row in res:
        #         joueur = Joueur(
        #             id_joueur=row["id_joueur"],
        #             pseudo=row["pseudo"],
        #             mdp=row["mdp"],
        #             age=row["age"],
        #             mail=row["mail"],
        #             fan_pokemon=row["fan_pokemon"],
        #         )

        #         liste_cocktails.append(joueur)

        # return liste_cocktails

    @log
    def cocktail_partiel(self, nb_manquants) -> list[Cocktail]:
        """Lister tous les cocktails que l'utilisateur peut préparer avec au plus n ingrédients manquants dans son inventaire

        Parameters
        ----------
        nb_manquants : int
            Nombre maximal d'ingrédients manquants autorisés pour préparer un cocktail.

        Returns
        -------
        list[Cocktail]
            Liste des cocktails que l'utilisateur peut préparer avec au plus nb_manquants ingrédients manquants.
        """

    #     res = None

    #     try:
    #         with DBConnection().connection as connection:
    #             with connection.cursor() as cursor:
    #                 cursor.execute(
    #                     "UPDATE joueur                                      "
    #                     "   SET pseudo      = %(pseudo)s,                   "
    #                     "       mdp         = %(mdp)s,                      "
    #                     "       age         = %(age)s,                      "
    #                     "       mail        = %(mail)s,                     "
    #                     "       fan_pokemon = %(fan_pokemon)s               "
    #                     " WHERE id_joueur = %(id_joueur)s;                  ",
    #                     {
    #                         "pseudo": joueur.pseudo,
    #                         "mdp": joueur.mdp,
    #                         "age": joueur.age,
    #                         "mail": joueur.mail,
    #                         "fan_pokemon": joueur.fan_pokemon,
    #                         "id_joueur": joueur.id_joueur,
    #                     },
    #                 )
    #                 res = cursor.rowcount
    #     except Exception as e:
    #         logging.info(e)

    #     return res == 1
