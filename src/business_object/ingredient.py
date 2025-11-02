class Ingredient:
    """
    Classe représentant un Ingredient

    Attributs
    ----------
    id_ingredient : int
        identifiant de l'ingredient
    nom_ingredient : str
        nom de l'ingrédient
    desc_ingredient : str
        description de l'ingrédient
    """

    def __init__(self, id_ingredient, nom_ingredient, desc_ingredient):
        """Constructeur"""
        self.id_ingredient = id_ingredient
        self.nom_ingredient = nom_ingredient
        self.desc_ingredient = desc_ingredient
