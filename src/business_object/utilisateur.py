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
    """

    def __init__(
        self,
        pseudo,
        mdp,
        age,
        langue,
        est_majeur=False,
        id_utilisateur=None,
    ):
        """Constructeur"""

        self.pseudo = pseudo
        self.mdp = mdp
        self.age = age
        self.langue = langue
        self.est_majeur = est_majeur
        self.id_utilisateur = id_utilisateur

    def __str__(self):
        """Permet d'afficher les informations de l'utilisateur"""
        return f"Utilisateur(id={self.id_utilisateur}, pseudo={self.pseudo})"
