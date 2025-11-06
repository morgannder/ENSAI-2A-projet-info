from datetime import datetime

class Commentaire:
    """
    Classe représentant un Commentaire de cocktail

    Attributs
    ----------
    id_commentaire : int
        identifiant du commentaire
    id_utilisateur : int
        identifiant de l'utilisateur
    id_cocktail : int
        identifiant du cocktail
    text: str
        commentaire
    note: int
        note du cocktail
    date_creation: str
        date de création du commentaire

    """
    def __init__(
        self,
        id_commentaire=None,
        id_utilisateur=None,
        id_cocktail=None,
        texte="",
        note=0,
        date_creation=None,
        pseudo_utilisateur=""
    ):
        self.id_commentaire = id_commentaire
        self.id_utilisateur = id_utilisateur
        self.id_cocktail = id_cocktail
        self.texte = texte
        self.note = note
        self.date_creation = date_creation or datetime.now()
        self.pseudo_utilisateur = pseudo_utilisateur

    def __str__(self):
        return f"Commentaire({self.id_commentaire}, user:{self.id_utilisateur}, cocktail:{self.id_cocktail})"
