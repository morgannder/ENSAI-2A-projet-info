import logging

from dao.db_connection import DBConnection
from business_object.ingredient import Ingredient
from utils.log_decorator import log
from utils.singleton import Singleton


class InventaireDao(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux ingrédients de la base de données"""

    @log
    def creer_ingredient(self, ingredient: Ingredient) -> bool:
        """
        Créer un ingrédient dans l'inventaire.

        Parameters
        ----------
        ingredient : Ingredient
            l'ingrédient que l'on souhaite ajouter dans l'inventaire

        Returns
        -------
        bool
            True si la création est un succès
            False sinon
        """
        if ingredient is None:
            return False
        nom= getattr(ingredient, "nom_ingredient",None) or getattr(ingredient,"nom",None)
        desc = getattr(ingredient, "desc_ingredient", None) or getattr(ingredient, "description", None)

        if not nom or not isinstance(nom, str):
            return False

        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO ingredient (nom_ingredient,desc_ingredient
                        VALUES (%(nom)s,%(desc)s)
                        RETURNING id_ingredient;
                        """,
                        {"nom":nom.strip(),"desc":desc},
                        )
                        res=cursor.fectchone()
        except Exception as e :
            logging.info(e)
        created = False
    if res:
        new_id = res["id_ingredient"] if isinstance(res, dict) else res[0]
        for attr in ("id_ingredient", "id"):
            if hasattr(ingredient, attr):
                setattr(ingredient, attr, new_id)
                break
        created = True



    @log
    def supprimer_ingredient(self, id_ingredient) -> bool:
        """
        Supprimer un ingrédient de l'inventaire.

        Parameters
        ----------
        id_ingredient : int
            l'id de l'ingredient à supprimé

        Returns
        -------
        bool
            True si la suppression est un succès
            False sinon
        """
        if ingredient is None:
            return False
        res=0
        try:
            with DBConnection().connection as connection
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM inventaire_ingredient
                         WHERE id_ingredient= %(id_ingredient)s;
                        """,
                        {"id_ingredient":id_ingredient},
                    )
                    cursor.execute(
                        """
                        DELETE FROM ingredient
                        WHERE id_ingredient = %(id_ingredient)s;
                        """,
                        {"id_ingredient":id_ingredient},
                    )
                    res= cursor.rowcount
        except Exception as e:
            logging.info(e)
        return res > 0
    @log
    def consulter_inventaire(self) -> list[Ingredient]:
        """
        Lister tous les ingrédients de l'inventaire.

        Parameters
        ----------
        None

        Returns
        -------
        liste_ingredients : list[Ingredient]
            Renvoie la liste de tous les ingrédients de l'inventaire.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor as cursor:
                    cursor.execute(
                        """
                        SELECT id_ingredient, nom_ingredient, desc_ingredient
                        FROM ingredient
                        ORDER BY LOWER(nom_ingredient):
                        """
                    )
                    rows=cursor.fetchall()
        except Exception as e:
            logging.info(e)
            rows=None

        liste_ingredients :list[Ingredient]=[]
        if rows:
            for r in rows:
                if isinstance(r,dict):
                    _id=r["id_ingredient"]
                    _nom=r["nom_ingredient"]
                    _desc=r.get("desc_ingredient")
        else :
            _id,_nom,_desc=r[0],r[1],r[2] if len(r)> else None
