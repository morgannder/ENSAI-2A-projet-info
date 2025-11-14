from business_object.commentaire import Commentaire
from dao.commentaire_dao import CommentaireDao
from utils.log_decorator import log


class CommentaireService:
    @log
    def ajouter_commentaire(
        self, id_utilisateur: int, id_cocktail: int, texte: str, note: int
    ) -> bool:
        """
        Ajoute un nouveau commentaire pour un cocktail donné

        Vérifie la validité du texte et de la note avant insertion
        Empêche un utilisateur de commenter deux fois le même cocktail

        Paramètres
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur qui laisse le commentaire
        id_cocktail : int
            Identifiant du cocktail commenté.
        texte : str
            Contenu du commentaire (ne peut pas être vide)
        note : int
            Note attribuée au cocktail, entre 1 et 5 inclus

        Retour
        -------
        bool
            True si le commentaire a été créé avec succès, False sinon
        """
        # Verification de la validité
        if not texte or len(texte.strip()) == 0:
            raise ValueError("Le commentaire ne peut pas être vide")
        if note < 1 or note > 5:
            raise ValueError("La note doit être entre 1 et 5")

        # On verifie si l'utilisateur à deja commenté
        existant = CommentaireDao().trouver_par_utilisateur_et_cocktail(id_utilisateur, id_cocktail)
        if existant:
            raise ValueError("Vous avez déjà commenté ce cocktail")

        commentaire = Commentaire(
            id_utilisateur=id_utilisateur, id_cocktail=id_cocktail, texte=texte.strip(), note=note
        )

        return CommentaireDao().creer(commentaire)

    @log
    def supprimer_commentaire(self, id_utilisateur: int, id_commentaire: int) -> bool:
        """
        Supprime un commentaire existant laissé par un utilisateur

        Paramètres
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur propriétaire du commentaire
        id_commentaire : int
            Identifiant du commentaire à supprimer

        Retour
        -------
        bool
            True si la suppression a réussi, False sinon (ex. : commentaire inexistant ou non autorisé).
        """
        return CommentaireDao().supprimer(id_commentaire, id_utilisateur)

    @log
    def lister_commentaires_cocktail(self, id_cocktail: int) -> list[Commentaire]:
        """
        Récupère la liste complète des commentaires associés à un cocktail

        Paramètres
        ----------
        id_cocktail : int
            Identifiant du cocktail dont on souhaite récupérer les commentaires

        Retour
        -------
        list[Commentaire]
            Liste des objets Commentaire correspondant au cocktail
            (Peut être vide si aucun commentaire n'est présent)
        """
        return CommentaireDao().trouver_par_cocktail(id_cocktail)

    @log
    def obtenir_commentaire_utilisateur(self, id_utilisateur: int, id_cocktail: int) -> Commentaire:
        """
        Récupère le commentaire laissé par un utilisateur sur un cocktail spécifique

        Paramètres
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur
        id_cocktail : int
            Identifiant du cocktail concerné

        Retour
        -------
        Commentaire or None
            L'objet Commentaire correspondant s'il existe, sinon None
        """
        return CommentaireDao().trouver_par_utilisateur_et_cocktail(id_utilisateur, id_cocktail)

    @log
    def obtenir_commentaires_par_utilisateur(self, id_utilisateur: int) -> list[Commentaire]:
        """
        Récupère tous les commentaires laissés par un utilisateur.

        Paramètres
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur dont on souhaite obtenir les commentaires

        Retour
        -------
        list[Commentaire]
            Liste des objets Commentaire associés à l'utilisateur.
            Peut être vide si l'utilisateur n'a encore rien commenté.
        """
        try:
            return CommentaireDao().trouver_par_utilisateur_et_cocktail(id_utilisateur)
        except Exception as e:
            print(f"Erreur récupération commentaires utilisateur: {e}")
            return []

    @log
    def calculer_note_moyenne(self, id_cocktail: int) -> float:
        """
        Calcule la note moyenne d’un cocktail à partir des commentaires existants

        Paramètres
        ----------
        id_cocktail : int
            Identifiant du cocktail dont on souhaite la note moyenne

        Retour
        -------
        float
            Note moyenne du cocktail
        """
        commentaires = self.lister_commentaires_cocktail(id_cocktail)
        if not commentaires:
            return 0.0
        return sum(com.note for com in commentaires) / len(commentaires)
