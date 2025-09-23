class Utilisateur:
    """
    Classe représentant un Joueur

    Attributs
    ----------
    id_joueur : int
        identifiant
    pseudo : str
        pseudo du joueur
    mdp : str
        le mot de passe du joueur
    age : int
        age du joueur
    mail : str
        mail du joueur
    fan_pokemon : bool
        indique si le joueur est un fan de Pokemon
    """

    def __init__(self, id_utilisateur, pseudo, mdp, age, langue):
        """Constructeur"""
        self.id_utilisateur = id_utilisateur
        self.pseudo = pseudo
        self.mdp = mdp
        self.age = age
        self.langue = langue

    def __str__(self):
        """Permet d'afficher les informations de l'utilisateur"""
        pass
