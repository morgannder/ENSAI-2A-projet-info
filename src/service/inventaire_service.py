from business_object.ingredient import Ingredient
from utils.log_decorator import log
from


class InventaireService:
    """Classe contenant les méthodes de service pour l'inventaire"""

    @log
    def lister_suggestion_ingredient(self, id_utilisateur) -> List[Ingredient]:
        """
        Créer un ingrédient dans l'inventaire.

        Parameters
        ----------
        nom_ingredient : str
            L'ingrédient à ajouter dans l'inventaire.

        Returns
        -------
        bool
            True si succès
            sinon False
        """
        # TODO: Appeler InventaireDao().creer_ingredient et retourner l'objet si succès
        # TODO: afficher à l'utilisateur (succès ou échec)

        pass

    @log
    def ajouter_ingredient(self, nom_ingredient=None, id_ingredient=None) -> bool:
        """
        Créer un ingrédient dans l'inventaire.

        Parameters
        ----------
        nom_ingredient : str
            L'ingrédient à ajouter dans l'inventaire.

        id_ingredient : str
            L'ingrédient à ajouter dans l'inventaire dans le cas où il rentre l'id à partir des
            suggestions faites par lister_suggestion_ingredient.

        Returns
        -------
        bool
            True si succès
            sinon False
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
    def consulter_inventaire(self, id_utilisateur) -> list[Ingredient]:
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
