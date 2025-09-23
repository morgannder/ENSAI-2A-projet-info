class Ingredient:
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

    def __init__(self, id_ingredient, nom_ingredient, desc_ingredient, age, langue):
        """Constructeur"""
        self.id_ingredient = id_ingredient
        self.nom_ingredient = nom_ingredient
        self.desc_ingredient = desc_ingredient
