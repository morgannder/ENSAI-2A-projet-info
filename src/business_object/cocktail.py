class Cocktail:
    """
    Classe représentant un Cocktail

    Attributs
    ----------
    id_cocktail : int
        identifiant du cocktail
    nom_cocktail : str
        nom du cocktail
    categ_cocktail : str
        categorie du cocktail
    image_cocktail : str
        chemin de l'image du cocktail
    alcoolise_cocktail : str
        indiqque si le cocktail est alcoolisé ou non ou optionnel
    instruc_cocktail : str
        instruction pour la réalisation du cocktail
    """

    def __init__(
        self,
        id_cocktail,
        nom_cocktail,
        categ_cocktail,
        image_cocktail,
        alcoolise_cocktail,
        instruc_cocktail,
    ):
        """Constructeur"""
        self.id_cocktail = id_cocktail
        self.nom_cocktail = nom_cocktail
        self.categ_cocktail = categ_cocktail
        self.image_cocktail = image_cocktail
        self.alcoolise_cocktail = alcoolise_cocktail
        self.instruc_cocktail = instruc_cocktail
