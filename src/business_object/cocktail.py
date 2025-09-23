class Cocktail:
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

    def __init__(self, id_cocktail, nom_cocktail, categ_cocktail, image_cocktail, alcoolise_cocktail,
                 instruc_cocktail):
        """Constructeur"""
        self.id_cocktail = id_cocktail
        self.nom_cocktail = nom_cocktail
        self.categ_cocktail = categ_cocktail
        self.image_cocktail = image_cocktail
        self.alcoolise_cocktail = alcoolise_cocktail
        self.instruc_cocktail = instruc_cocktail
