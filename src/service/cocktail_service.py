from business_object.cocktail import Cocktail
from dao.cocktail_dao import CocktailDao
from utils.log_decorator import log


class CocktailService:
    """Classe contenant les méthodes de service pour les cocktails."""

    @log
    def rechercher_par_filtre(self, nom_cocktail=None, categ=None, alcool=None,
                              ingredient=None) -> list[Cocktail]:
        """
        Recherche les cocktails dont le nom contient la chaîne donnée.

        Parameters
        ----------
        nom_cocktail : str
            Nom ou partie du nom du cocktail à rechercher.

        Returns
        -------
        list[Cocktail]
            Liste des cocktails dont le nom correspond à la recherche.
        """
        # TODO: Afficher un message à l'utilisateur si aucun cocktail n'est trouvé
        return CocktailDao().rechercher_cocktail_par_mon(nom_cocktail)

    @log
    def lister_cocktails_complets(self, id_utilisateur) -> list[Cocktail]:
        """
        Liste tous les cocktails que l'utilisateur peut préparer
        avec tous les ingrédients disponibles dans son inventaire.

        Returns
        -------
        list[Cocktail]
            Liste de tous les cocktails complets.
        """
        # TODO: Implémenter la récupération via CocktailDao.cocktail_complet
        pass

    @log
    def lister_cocktails_partiels(self, id_utilisateur, nb_manquants) -> list[Cocktail]:
        """
        Liste tous les cocktails que l'utilisateur peut préparer avec au plus un certain nombre d'ingrédients manquants.

        Parameters
        ----------
        nb_manquants : int
            Nombre maximal d'ingrédients manquants autorisés.

        Returns
        -------
        list[Cocktail]
            Liste des cocktails que l'utilisateur peut préparer avec au plus nb_manquants ingrédients manquants.
        """
        # TODO: Implémenter la récupération via CocktailDao.cocktail_partiel
        pass
