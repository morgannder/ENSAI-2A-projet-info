from business_object.cocktail import Cocktail
from dao.cocktail_dao import CocktailDao
from utils.log_decorator import log


class CocktailService:
    """Classe contenant les méthodes de service pour les cocktails."""

    def _filter_cocktails_for_minor(self, cocktails):
        """Filtre les cocktails pour ne garder que les non alcoolisés."""
        return [c for c in cocktails if c.alcoolise_cocktail == "Non alcoholic"]

    @log
    def rechercher_par_filtre(
        self,
        est_majeur=None,
        nom_cocktail=None,
        categ=None,
        alcool=None,
        liste_ingredients=None,
        verre=None,
        langue=None,
        limit=10,
        offset=0,
    ) -> list[Cocktail]:
        """
        Recherche les cocktails selon différents filtres.

        Parameters
        ----------
        est_majeur : bool, optional
            Si majeur ou pas, filtre automatiquement les cocktails non alcoolisés.
        nom_cocktail : str, optional
            Nom ou partie du nom du cocktail à rechercher.
        categ : str, optional
            Catégorie du cocktail.
        alcool : str, optional
            Type d'alcool ("Alcoholic", "Non alcoholic", "Optional alcohol").
        liste_ingredients : list[str], optional
            Liste des ingrédients que le cocktail doit contenir (tous requis).
        verre : str, optional
            Verre utilisé.
        langue : str
           Langue de l'utilisateur ("FR", "EN", 'ES").
        limit : int, optional
            Nombre maximum de résultats (défaut: 10).
        offset : int, optional
            Décalage pour la pagination (défaut: 0).

        Returns
        -------
        list[Cocktail]
            Liste des cocktails correspondant aux critères.

        Raises
        ------
        ValueError
            Si le type d'alcool est invalide ou si l'utilisateur est introuvable.
            Si l'utilisateur mineur veut appliquer un filtre Alcoholic.
        """

        # Traitement de la réponse du type d'alcool pour avoir "Alcoholic", "Non alcoholic", "Optional alcohol"

        if alcool:
            alcool = alcool[0].upper() + alcool[1:].lower()
            print(alcool)

            # Validation du type d'alcool
            if alcool not in ["Alcoholic", "Non alcoholic", "Optional alcohol"]:
                raise ValueError(
                    "Le type d'alcool doit être 'Alcoholic', 'Non alcoholic' ou 'Optional alcohol'"
                )

        # Validation catégories
        if categ:
            categories_valides = CocktailDao().lister_categories()
            if categ not in categories_valides:
                raise ValueError(
                    f"La catégorie '{categ}' n'existe pas. "
                    f"Utilisez GET /cocktails/categories pour voir les catégories disponibles."
                )

        # Validation du type de verre
        if verre:
            verres_valides = CocktailDao().lister_verres()
            if verre not in verres_valides:
                raise ValueError(
                    f"Le verre '{verre}' n'existe pas. "
                    f"Utilisez GET /cocktails/verres pour voir les verres disponibles."
                )

        # Si mineur, lui interdire le filtre Alcoholic
        if est_majeur is False and alcool == "Alcoholic":
            raise ValueError(
                " Zéro alcool pour les mineurs ici, mais 100% fun garanti avec nos cocktails non alcolisé 😎🍹"
            )

        cocktails = CocktailDao().rechercher_cocktails(
            nom_cocktail, categ, verre, alcool, liste_ingredients, langue, limit, offset
        )
        return cocktails if cocktails else []

    @log
    def lister_cocktails_complets(
        self, id_utilisateur, est_majeur, limit=10, offset=0
    ) -> list[Cocktail]:
        """
        Liste tous les cocktails que l'utilisateur peut préparer
        avec tous les ingrédients disponibles dans son inventaire.

        Parameters
        ----------
        id_utilisateur : int
            ID de l'utilisateur.
        est_majeur : bool
            Si majeur ou pas, filtre automatiquement les cocktails non alcoolisés.
        limit : int, optional
            Nombre maximum de résultats (défaut: 10).
        offset : int, optional
            Décalage pour la pagination (défaut: 0).

        Returns
        -------
        list[Cocktail]
            Liste de tous les cocktails complets.

        Raises
        ------
        ValueError
            Si l'ID utilisateur est manquant ou invalide.
        """
        if not id_utilisateur:
            raise ValueError("La connexion est requise pour accéder à l'inventaire")

        cocktails = CocktailDao().cocktail_complet(id_utilisateur, limit, offset)

        # Filtrer si mineur
        if est_majeur is False:
            cocktails = self._filter_cocktails_for_minor(cocktails)

        return cocktails if cocktails else []

    @log
    def lister_cocktails_partiels(
        self, nb_manquants, id_utilisateur, est_majeur, limit=10, offset=0
    ) -> list[Cocktail]:
        """
        Liste tous les cocktails que l'utilisateur peut préparer avec au plus
        un certain nombre d'ingrédients manquants.

        Parameters
        ----------
        nb_manquants : int
            Nombre maximal d'ingrédients manquants autorisés.
        id_utilisateur : int
            ID de l'utilisateur.
        est_majeur : bool
            Si majeur ou pas, filtre automatiquement les cocktails non alcoolisés.
        limit : int, optional
            Nombre maximum de résultats (défaut: 10).
        offset : int, optional
            Décalage pour la pagination (défaut: 0).

        Returns
        -------
        list[Cocktail]
            Liste des cocktails réalisables avec au plus nb_manquants ingrédients manquants.

        Raises
        ------
        ValueError
            Si nb_manquants est négatif, si l'ID utilisateur est manquant ou invalide.
        """
        if nb_manquants < 0 or nb_manquants > 5:
            raise ValueError("Le nombre d'ingrédients manquants doit être compris entre 0 et 5")

        if not id_utilisateur:
            raise ValueError("La connexion est requise pour accéder à l'inventaire")

        cocktails = CocktailDao().cocktail_partiel(id_utilisateur, nb_manquants, limit, offset)

        # Filtrer si mineur
        if est_majeur is False:
            cocktails = self._filter_cocktails_for_minor(cocktails)

        return cocktails if cocktails else []

    @log
    def cocktails_aleatoires(self, est_majeur=None, nb=5) -> list[Cocktail]:
        """
        Récupérer une liste de cocktails aléatoires.

        Parameters
        ----------
        est_majeur : bool, optional
            Si majeur ou pas, filtre automatiquement les cocktails non alcoolisés.
        nb : int, optional
            Nombre de cocktails souhaités (défaut: 5, maximum: 5).

        Returns
        -------
        list[Cocktail]
            Liste de cocktails aléatoires (entre 1 et 5 cocktails).

        Raises
        ------
        ValueError
            Si le nombre n'est pas entre 1 et 5.
        """
        if nb < 1 or nb > 5:
            raise ValueError("Le nombre de cocktails doit être entre 1 et 5")

        # Dans tous les cas on ne renverra pas plus de 5
        nb_limite = min(nb, 5)
        cocktails = CocktailDao().cocktails_aleatoires(nb_limite)

        # Filtrer si mineur
        if est_majeur is False:
            cocktails = self._filter_cocktails_for_minor(cocktails)

        return cocktails if cocktails else []

    @log
    def obtenir_cocktail_par_id(self, id_cocktail) -> Cocktail:
        """
        Récupérer un cocktail par son ID.

        Parameters
        ----------
        id_cocktail : int
            ID du cocktail recherché.

        Returns
        -------
        Cocktail
            Le cocktail trouvé si succès, None sinon.

        Raises
        ------
        ValueError
            Si l'ID du cocktail est invalide.
        """
        if not isinstance(id_cocktail, int) or id_cocktail <= 0:
            raise ValueError("L'ID du cocktail doit être un entier positif")

        cocktail = CocktailDao().trouver_par_id(id_cocktail)

        if not cocktail:
            return None

        return cocktail

    @log
    def lister_tous_cocktails(self) -> list[Cocktail]:
        """
        Récupérer la liste complète de tous les cocktails.

        Returns
        -------
        list[Cocktail]
            Liste de tous les cocktails disponibles.
        """
        cocktails = CocktailDao().lister_tous()
        return cocktails if cocktails else []

    @log
    def lister_categories(self) -> list[str]:
        """
        Liste toutes les catégories de cocktails disponibles.

        Returns
        -------
        list[str]
            Liste des catégories uniques, triées alphabétiquement.
        """
        categories = CocktailDao().lister_categories()
        return categories if categories else []

    @log
    def lister_verres(self) -> list[str]:
        """
        Liste tous les types de verres disponibles.

        Returns
        -------
        list[str]
            Liste des types de verres uniques, triés alphabétiquement.
        """
        verres = CocktailDao().lister_verres()
        return verres if verres else []
