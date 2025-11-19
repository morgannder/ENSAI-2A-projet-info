from typing import List

from business_object.ingredient import Ingredient
from dao.inventaire_dao import InventaireDao


class InventaireService:
    def lister(self, id_utilisateur: int) -> List[Ingredient]:
        """Renvoie une liste des ingrédients de l'inventaire.

        Paramètres
        ----------
        id_utilisateur: int
            L'id associé à l'utilisateur.

        Retour
        -------
        List[Ingredient]
            Renvoie une liste de l'ensemble des ingrédient de l'inventaire.

        Raises
        -------
        ValueError
            Si l'inventaire est vide

        """
        if not isinstance(id_utilisateur, int):
            raise TypeError("L'id rentré n'est pas valide")
        inventaire = InventaireDao().consulter_inventaire(id_utilisateur)
        if inventaire == []:
            raise ValueError(
                "Votre inventaire est vide, allez le remplir au plus vite !!"
            )
        return inventaire

    def ajouter(self, id_utilisateur: int, ingredient: Ingredient) -> bool:
        """Ajoute un ingrédient dans l'inventaire de l'utilisateur.

        Paramètres
        ----------
        id_utilisateur: int
            L'id associé à l'utilisateur.
        ingredient: Ingredient

        Retour
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

        Paramètres
        ----------
        id_utilisateur: int
            L'id associé à l'utilisateur
        id_ingredient: int
            L'id associé à l'ingredient

        Retour
        -------
        created : bool
            True si la suppression est un succès
            False sinon
        """
        return InventaireDao().supprimer_ingredient(id_utilisateur, id_ingredient)

    def recherche_ingredient(self, ingredient: str) -> Ingredient:
        """
        Recherche un ingrédient grâce à son nom et renvoie un type Ingredient

        Paramètres
        ----------
        ingredient : str
            Nom de l'ingrédient à rechercher.

        Retour
        -------
        ingredient : Ingredient
        """
        return InventaireDao().recherche_ingredient(ingredient)

    def suggerer_ingredients(self, n: int = 5):
        """
        Retourne entre 1 et n ingrédients aléatoires pour informer
        l'utilisateur des catégories existantes.

        Paramètres
        ----------
        n : int
            Le nombre de suggestions voulues.

        Retour
        -------
        List[Ingredient]
            Une liste d'ingrédients aléatoire.
        """
        if not isinstance(n, int):
            raise ValueError(
                f"Le paramètre 'n' doit être un entier, reçu : {type(n).__name__}"
            )
        if n < 1:
            n = 1
        elif n > 10:
            n = 10
        return InventaireDao().ingredients_aleatoires(n)
