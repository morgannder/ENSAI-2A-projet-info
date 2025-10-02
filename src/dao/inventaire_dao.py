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
        # TODO: Implémenter la création d'un ingrédient
        pass

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
        # TODO: Implémenter la suppression d'un ingrédient
        pass

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
        # TODO: Implémenter la consultation de l'inventaire
        pass
