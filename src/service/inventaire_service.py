from typing import List

from business_object.ingredient import Ingredient
from dao.inventaire_dao import InventaireDao


class InventaireService:
    def lister(self, id_utilisateur: int) -> List[Ingredient]:
        """Renvoie une liste des ingrédients de l'inventaire.

        Parameters
        ----------
        id_utilisateur: int
            L'id associé à l'utilisateur.

        Returns
        -------
        List[Ingredient]
            Renvoie une liste de l'ensemble des ingrédient de l'inventaire.

        """
        if not isinstance(id_utilisateur, int) or id_utilisateur <= 0:
            return []
        return InventaireDao().consulter_inventaire(id_utilisateur)

    def ajouter(self, id_utilisateur: int, ingredient: Ingredient) -> bool:
        """Ajoute un ingrédient dans l'inventaire de l'utilisateur.

        Parameters
        ----------
        id_utilisateur: int
            L'id associé à l'utilisateur.
        ingredient: Ingredient

        Returns
        -------
        created : bool
            True si l'ingrédient a bien été ajouté.
            False sinon
        """
        if not isinstance(ingredient, Ingredient):
            return False
        return InventaireDao().ajouter_ingredient_inventaire(id_utilisateur, ingredient)

    def supprimer(self, id_utilisateur: int, id_ingredient: int) -> bool:
        """Permet de supprimer l'ingrédient de l'inventaire d'un utilisateur

        Parameters
        ----------
        id_utilisateur: int
            L'id associé à l'utilisateur
        id_ingredient: int
            L'id associé à l'ingredient

        Returns
        -------
        created : bool
            True si la suppression est un succès
            False sinon
        """
        return InventaireDao().supprimer_ingredient(id_utilisateur, id_ingredient)

    def recherche_ingredient(self, ingredient: str) -> Ingredient:
        """
        Recherche un ingrédient grâce à son nom et renvoie un type Ingredient

        Parameters
        ----------
        ingredient : str
            Nom de l'ingrédient à rechercher.

        Returns
        -------
        ingredient : Ingredient
        """
        return InventaireDao().recherche_ingredient(ingredient)

    def suggerer_ingredients(self, n: int = 5):
        """
        Retourne entre 1 et n ingrédients aléatoires pour informer
        l'utilisateur des catégories existantes.

        Parameters
        ----------
        n : int
            Le nombre de suggestions voulues.

        Returns
        -------
        List[Ingredient]
            Une liste d'ingrédients aléatoire.
        """
        if not isinstance(n, int):
            raise ValueError(f"Le paramètre 'n' doit être un entier, reçu : {type(n).__name__}")
        if n < 1:
            n = 1
        elif n > 10:
            n = 10
        return InventaireDao().ingredients_aleatoires(n)
