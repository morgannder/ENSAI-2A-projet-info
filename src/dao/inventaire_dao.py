import logging
from typing import List, Optional

from dao.db_connection import DBConnection
from business_object.ingredient import Ingredient
from utils.log_decorator import log
from utils.singleton import Singleton


class InventaireDao(metaclass=Singleton):
    """Accès aux ingrédients de la base de données."""

    @log
    def ajouter_ingredient_inventaire(
        self, id_utilisateur: int, ingredient: Ingredient
    ) -> bool:
        if not isinstance(id_utilisateur, int) or id_utilisateur <= 0:
            return False
        if (
            ingredient is None
            or not isinstance(ingredient.nom_ingredient, str)
            or not ingredient.nom_ingredient.strip()
        ):
            return False

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # 1) Récupérer/créer l'ingrédient si pas d'id
                    if ingredient.id_ingredient is None:
                        cursor.execute(
                            """
                            SELECT id_ingredient
                            FROM ingredient
                            WHERE lower(nom_ingredient) = lower(%(nom)s);
                            """,
                            {"nom": ingredient.nom_ingredient.strip()},
                        )
                        row = cursor.fetchone()
                        if row:
                            ing_id = (
                                row["id_ingredient"]
                                if isinstance(row, dict)
                                else row[0]
                            )
                        else:
                            cursor.execute(
                                """
                                INSERT INTO ingredient (nom_ingredient, desc_ingredient)
                                VALUES (%(nom)s, %(desc)s)
                                RETURNING id_ingredient;
                                """,
                                {
                                    "nom": ingredient.nom_ingredient.strip(),
                                    "desc": getattr(
                                        ingredient, "desc_ingredient", None
                                    ),
                                },
                            )
                            row = cursor.fetchone()
                            if not row:
                                return False
                            ing_id = (
                                row["id_ingredient"]
                                if isinstance(row, dict)
                                else row[0]
                            )
                            ingredient.id_ingredient = int(ing_id)
                    else:
                        ing_id = int(ingredient.id_ingredient)

                    # 2) Lier à l'inventaire utilisateur (éviter doublons)
                    cursor.execute(
                        """
                        INSERT INTO inventaire_ingredient (id_ingredient, id_utilisateur)
                        VALUES (%(id_ing)s, %(id_user)s)
                        ON CONFLICT (id_ingredient, id_utilisateur) DO NOTHING;
                        """,
                        {"id_ing": ing_id, "id_user": id_utilisateur},
                    )
                    return True
        except Exception as e:
            logging.exception("Erreur lors de l'ajout à l'inventaire: %s", e)
            return False

    @log
    def supprimer_ingredient(self, id_utilisateur: int, id_ingredient: int) -> bool:
        if not isinstance(id_utilisateur, int) or id_utilisateur <= 0:
            return False
        if not isinstance(id_ingredient, int) or id_ingredient <= 0:
            return False

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM inventaire_ingredient
                        WHERE id_utilisateur = %(idu)s
                          AND id_ingredient = %(idi)s;
                        """,
                        {"idu": id_utilisateur, "idi": id_ingredient},
                    )
                    deleted = cursor.rowcount
        except Exception as e:
            logging.exception(
                "Erreur lors de la suppression d'un ingrédient de l'inventaire utilisateur: %s",
                e,
            )
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
            logging.exception(
                "Erreur lors de la consultation de l'inventaire utilisateur: %s", e
            )
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
