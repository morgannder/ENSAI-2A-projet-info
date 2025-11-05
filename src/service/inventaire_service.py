from typing import List

from business_object.ingredient import Ingredient
from dao.inventaire_dao import InventaireDao


class InventaireService:
    def lister(self, id_utilisateur: int) -> List[Ingredient]:
        """
        Retourne la liste des ingrédients de l'utilisateur.
        """
        if not isinstance(id_utilisateur, int) or id_utilisateur <= 0:
            return []
        return InventaireDao().consulter_inventaire(id_utilisateur)

    def ajouter(self, id_utilisateur: int, ingredient: Ingredient) -> bool:
        """
        Ajoute un ingrédient (création si besoin) puis le lie à l'utilisateur.
        """
        if not isinstance(ingredient, Ingredient):
            return False
        return InventaireDao().ajouter_ingredient_inventaire(id_utilisateur, ingredient)

    def supprimer(self, id_utilisateur: int, id_ingredient: int) -> bool:
        """
        Supprime un ingrédient du stock personnel de l'utilisate.
        """
        return InventaireDao().supprimer_ingredient(id_utilisateur, id_ingredient)

    def recherche_ingredient(self, ingredient: str) -> Ingredient:
        """
        Recherche un ingrédient grâce à son nom et renvoie un type Ingredient
        """
        return InventaireDao().recherche_ingredient(ingredient)

    def suggerer_ingredients(self, n: int = 5):
        """
        Retourne entre 1 et n ingrédients aléatoires pour suggestion.
        """
        if not isinstance(n, int):
            raise ValueError(f"Le paramètre 'n' doit être un entier, reçu : {type(n).__name__}")
        if n < 1:
            n = 1
        elif n > 10:
            n = 10
        return InventaireDao().ingredients_aleatoires(n)
