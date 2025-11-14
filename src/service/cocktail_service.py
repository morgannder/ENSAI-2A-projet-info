import logging

from business_object.cocktail import Cocktail
from business_object.cocktail_complet import CocktailComplet
from dao.cocktail_dao import CocktailDao
from utils.log_decorator import log


class CocktailService:
    """Classe contenant les méthodes de service pour les cocktails."""

    def _filter_cocktails_pour_mineurs(self, cocktails):
        """
        Filtre les cocktails pour ne garder que les non alcoolisés.

        """
        return [c for c in cocktails if c.alcoolise_cocktail == "Non alcoholic"]

    @log
    def realiser_cocktail(
        self, id_cocktail: int = None, nom_cocktail: str = None, langue: str = "ENG"
    ) -> CocktailComplet:
        """Obtenir les détails d'un cocktail par ID ou nom.

        Paramètres
        ----------
        id_cocktail : int, optional
            Identifiant du cocktail.
        nom_cocktail : str, optional
            Nom du cocktail (insensible à la casse).
        langue : str
            Langue des instructions.

        """

        cocktail = CocktailDao().realiser_cocktail(
            id_cocktail=id_cocktail, nom_cocktail=nom_cocktail, langue=langue
        )

        if not cocktail:
            raise ValueError(" Zéro cocktail trouvé")

        return cocktail

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
        limite=10,
        decalage=0,
    ) -> list[Cocktail]:
        """
        Recherche les cocktails selon différents filtres.

        Paramètres
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
           Langue de l'utilisateur.
        limite : int, optional
            Nombre maximum de résultats (défaut: 10).
        decalage : int, optional
            Décalage pour la pagination (défaut: 0).

        Retour
        -------
        list[Cocktail]
            Liste des cocktails correspondant aux critères.

        Raises
        ------
        ValueError
            Si le type d'alcool est invalide ou si l'utilisateur est introuvable.
            Si l'utilisateur mineur veut appliquer un filtre Alcoholic.
        """

        # Validation du type d'alcool
        alcool_liste = ["Alcoholic", "Non alcoholic", "Optional alcohol"]
        alcool_valide = [alcool.lower() for alcool in alcool_liste]
        if alcool and alcool.lower() not in alcool_valide:
            raise ValueError(
                "Le type d'alcool doit être 'Alcoholic', 'Non alcoholic' ou 'Optional alcohol'"
            )

        # Si mineur, lui interdire le filtre Alcoholic
        if est_majeur is False and alcool == "Alcoholic":
            raise ValueError(
                " Zéro alcool pour les mineurs ici, mais 100% fun garanti avec nos cocktails non alcolisé 😎🍹"
            )

        cocktails = CocktailDao().rechercher_cocktails(
            nom_cocktail, categ, verre, alcool, liste_ingredients, langue, limite, decalage
        )

        # Filtrer si mineur
        if est_majeur is False:
            cocktails = self._filter_cocktails_pour_mineurs(cocktails)

        return cocktails if cocktails else []

    @log
    def lister_cocktails_complets(
        self, id_utilisateur, est_majeur, langue=None, limite=10, decalage=0
    ) -> list[Cocktail]:
        """
        Liste tous les cocktails que l'utilisateur peut préparer
        avec tous les ingrédients disponibles dans son inventaire.

        Paramètres
        ----------
        id_utilisateur : int
            ID de l'utilisateur.
        est_majeur : bool
            Si majeur ou pas, filtre automatiquement les cocktails non alcoolisés.
        langue : str
           Langue de l'utilisateur.
        limite : int, optional
            Nombre maximum de résultats (défaut: 10).
        decalage : int, optional
            Décalage pour la pagination (défaut: 0).

        Retour
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

        cocktails = CocktailDao().cocktail_complet(id_utilisateur, langue, limite, decalage)

        # Filtrer si mineur
        if est_majeur is False:
            cocktails = self._filter_cocktails_pour_mineurs(cocktails)

        return cocktails if cocktails else []

    @log
    def lister_cocktails_partiels(
        self, nb_manquants, id_utilisateur, est_majeur, langue=None, limite=10, decalage=0
    ) -> list[Cocktail]:
        """
        Liste tous les cocktails que l'utilisateur peut préparer avec au plus
        un certain nombre d'ingrédients manquants.

        Paramètres
        ----------
        nb_manquants : int
            Nombre maximal d'ingrédients manquants autorisés.
        id_utilisateur : int
            ID de l'utilisateur.
        est_majeur : bool
            Si majeur ou pas, filtre automatiquement les cocktails non alcoolisés.
        langue : str
           Langue de l'utilisateur.
        limite : int, optional
            Nombre maximum de résultats (défaut: 10).
        decalage : int, optional
            Décalage pour la pagination (défaut: 0).

        Retour
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

        cocktails = CocktailDao().cocktail_partiel(
            id_utilisateur, nb_manquants, langue, limite, decalage
        )

        # Filtrer si mineur
        if est_majeur is False:
            cocktails = self._filter_cocktails_pour_mineurs(cocktails)

        return cocktails if cocktails else []

    @log
    def cocktails_aleatoires(self, est_majeur=None, nb=5, langue=None) -> list[Cocktail]:
        """
        Récupérer une liste de cocktails aléatoires.

        Paramètres
        ----------
        est_majeur : bool, optional
            Si majeur ou pas, filtre automatiquement les cocktails non alcoolisés.
        nb : int, optional
            Nombre de cocktails souhaités (défaut: 5, maximum: 5).
        langue : str
           Langue de l'utilisateur.

        Retour
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
        cocktails = CocktailDao().cocktails_aleatoires(nb_limite, langue)

        # Filtrer si mineur
        if est_majeur is False:
            cocktails = self._filter_cocktails_pour_mineurs(cocktails)

        return cocktails if cocktails else []

    @log
    def obtenir_cocktail_par_id(self, id_cocktail) -> Cocktail:
        """
        Récupérer un cocktail par son ID.

        Paramètres
        ----------
        id_cocktail : int
            ID du cocktail recherché.

        Retour
        -------
        Cocktail
            Le cocktail trouvé si succès, None sinon.

        Raises
        ------
        ValueError
            Si l'ID du cocktail est invalide.
        """
        if not isinstance(id_cocktail, int) or id_cocktail < 0:
            raise ValueError("L'ID du cocktail doit être un entier positif")

        cocktail = CocktailDao().trouver_par_id(id_cocktail)

        if not cocktail:
            return None

        return cocktail

    @log
    def lister_tous_cocktails(self) -> list[Cocktail]:
        """
        Récupérer la liste complète de tous les cocktails.

        Retour
        -------
        list[Cocktail]
            Liste de tous les cocktails disponibles.
        """
        cocktails = CocktailDao().lister_tous()
        return cocktails if cocktails else []

    @log
    def obtenir_ingredients_par_cocktails(self, id_cocktails: list[int]) -> dict[int, list[str]]:
        """
        Récupère tous les ingrédients pour une liste de cocktails

        Paramètres
        ----------
        id_cocktails : list[int]
            ID des cocktails recherchés

        Retour
        -------
        dict { int : list[str] }
            Dictionnaire avec la liste des ingrédients nécessaire pour chaque cocktails
        """
        if not id_cocktails:
            return {}

        try:
            return CocktailDao().obtenir_ingredients_par_cocktails(id_cocktails)
        except Exception as e:
            logging.error(f"Erreur dans get_ingredients_par_cocktails: {str(e)}")
            return {}

    @log
    def obtenir_ingredients_possedes_par_cocktails(
        self, id_utilisateur: int, id_cocktails: list[int]
    ) -> dict[int, list[str]]:
        """
        Récupère les ingrédients possédés par l'utilisateur pour chaque cocktail

        Paramètres
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur
        id_cocktails : list[int]
            ID des cocktails recherchés

        Retour
        -------
        dict { int : list[str] }
            Dictionnaire avec la liste des ingrédients nécessaire pour chaque cocktails
        """
        if not id_cocktails:
            return {}

        try:
            return CocktailDao().obtenir_ingredients_possedes_par_cocktails(
                id_utilisateur=id_utilisateur, id_cocktails=id_cocktails
            )
        except Exception as e:
            logging.error(f"Erreur dans obtenir_ingredients_possedes_par_cocktails: {str(e)}")
            return {}
