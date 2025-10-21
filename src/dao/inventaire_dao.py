import logging
from typing import List, Optional

from dao.db_connection import DBConnection
from business_object.ingredient import Ingredient
from utils.log_decorator import log
from utils.singleton import Singleton


class InventaireDao(metaclass=Singleton):
    """Accès aux ingrédients de la base de données."""

    @log
    def creer_ingredient(self, ingredient: Ingredient) -> bool:
        """
        Créer un ingrédient dans l'inventaire global.
        Attend: Ingredient(id_ingredient: Optional[int], nom_ingredient: str, desc_ingredient: Optional[str])
        """
        if ingredient is None:
            return False
        if not isinstance(ingredient.nom_ingredient, str) or not ingredient.nom_ingredient.strip():
            return False

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO ingredient (nom_ingredient, desc_ingredient)
                        VALUES (%(nom)s, %(desc)s)
                        RETURNING id_ingredient;
                        """,
                        {"nom": ingredient.nom_ingredient.strip(), "desc": ingredient.desc_ingredient},
                    )
                    row = cursor.fetchone()
        except Exception as e:
            logging.exception("Erreur lors de la création d'un ingrédient: %s", e)
            return False

        if not row:
            return False

        new_id = row["id_ingredient"] if isinstance(row, dict) else row[0]
        try:
            ingredient.id_ingredient = int(new_id)  # affectation directe
        except Exception:
            return False

        return True

    @log
    def supprimer_ingredient(self, id_ingredient: int) -> bool:
        """
        Supprimer un ingrédient de l'inventaire global.
        """
        if not isinstance(id_ingredient, int):
            return False

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # Supprimer d'abord les références éventuelles côté utilisateurs
                    try:
                        cursor.execute(
                            "DELETE FROM inventaire_ingredient WHERE id_ingredient = %(id)s;",
                            {"id": id_ingredient},
                        )
                    except Exception:
                        # si la table n'existe pas (selon contexte), on ignore
                        pass

                    cursor.execute(
                        "DELETE FROM ingredient WHERE id_ingredient = %(id)s;",
                        {"id": id_ingredient},
                    )
                    deleted = cursor.rowcount
        except Exception as e:
            logging.exception("Erreur lors de la suppression d'un ingrédient: %s", e)
            return False

        return deleted > 0

    @log
    def consulter_inventaire(self, id_utilisateur: int) -> List[Ingredient]:
        """
        Lister les ingrédients de l'inventaire d'un utilisateur donné.

        Parameters
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur.

        Returns
        -------
        list[Ingredient]
            Ingrédients associés à cet utilisateur, triés par nom.
        """
        if not isinstance(id_utilisateur, int):
            return []

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT i.id_ingredient, i.nom_ingredient, i.desc_ingredient
                        FROM inventaire_ingredient ii
                        JOIN ingredient i ON i.id_ingredient = ii.id_ingredient
                        WHERE ii.id_utilisateur = %(idu)s
                        ORDER BY LOWER(i.nom_ingredient);
                        """,
                        {"idu": id_utilisateur},
                    )
                    rows = cursor.fetchall()
        except Exception as e:
            logging.exception("Erreur lors de la consultation de l'inventaire utilisateur: %s", e)
            rows = None

        if not rows:
            return []

        result: List[Ingredient] = []
        for r in rows:
            if isinstance(r, dict):
                _id = r["id_ingredient"]
                _nom = r["nom_ingredient"]
                _desc: Optional[str] = r["desc_ingredient"]
            else:
                _id = r[0]
                _nom = r[1]
                _desc = r[2] if len(r) > 2 else None

            ingredient = Ingredient(
                id_ingredient=int(_id) if _id is not None else None,
                nom_ingredient=_nom,
                desc_ingredient=_desc,
            )
            result.append(ingredient)

        return result
