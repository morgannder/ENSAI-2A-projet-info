class Utilisateur:
    """
    Classe représentant un Utilisateur

    Attributs
    ----------
    id_utilisateur : int
        identifiant de l'utilisateur
    pseudo : str
        pseudo de l'utilisateur
    mdp : str
        le mot de passe de l'utilisateur
    age : int
        age de l'utilisateur
    langue : str
        langue souhaité par l'utilisateur pour les recettes de cocktail
    cocktails_recherches : int
        Nombre de recherches de cocktail
    date_creation : str
        la date de création du compte de l'utilisateur
    """

    def __init__(
        self,
        pseudo,
        mdp,
        age,
        langue,
        cocktails_recherches,
        est_majeur=False,
        date_creation=None,
        id_utilisateur=None,
    ):
        """Constructeur"""

        self.pseudo = pseudo
        self.mdp = mdp
        self.age = age
        self.langue = langue
        self.est_majeur = est_majeur
        self.date_creation = date_creation
        self.id_utilisateur = id_utilisateur
        self.cocktails_recherches = cocktails_recherches

    def __str__(self):
        """Permet d'afficher les informations de l'utilisateur"""
        return f"Utilisateur(id={self.id_utilisateur}, pseudo={self.pseudo})"
