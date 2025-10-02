from business_object.ingredient import Ingredient
from utils.log_decorator import log


class InventaireService:
    """Classe contenant les méthodes de service pour l'inventaire"""

    @log
    def ajouter_ingredient(self, ingredient) -> Ingredient:
        """
        Créer un ingrédient dans l'inventaire.

        Parameters
        ----------
        ingredient : Ingredient
            L'ingrédient à ajouter dans l'inventaire.

        Returns
        -------
        Ingredient
            L'ingrédient créé si succès
            sinon None
        """
        # TODO: Appeler InventaireDao().creer_ingredient et retourner l'objet si succès
        # TODO: afficher à l'utilisateur (succès ou échec)

        pass

    @log
    def supprimer_ingredient(self, id_ingredient) -> bool:
        """
        Supprimer un ingrédient de l'inventaire.

        Parameters
        ----------
        id_ingredient : int
            L'identifiant de l'ingrédient à supprimer.

        Returns
        -------
        bool
            True si la suppression a réussi
            False sinon
        """
        # TODO: Appeler InventaireDao().supprimer_ingredient et retourner True/False
        # TODO: afficher à l'utilisateur (succès ou échec)

        pass

    @log
    def consulter_inventaire(self) -> list[Ingredient]:
        """
        Consulter tous les ingrédients de l'inventaire.

        Parameters
        ----------
        None

        Returns
        -------
        list[Ingredient]
            Liste de tous les ingrédients présents dans l'inventaire.
        """
        # TODO: Appeler InventaireDao().consulter_inventaire et retourner la liste
        pass
