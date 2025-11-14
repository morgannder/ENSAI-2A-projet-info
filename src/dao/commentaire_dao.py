from business_object.commentaire import Commentaire
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class CommentaireDao(metaclass=Singleton):
    @log
    def creer(self, commentaire: Commentaire) -> bool:
        """
        Crée un nouveau commentaire dans la base de données.

        Paramètres
        ----------
        commentaire : Commentaire
            Objet Commentaire à insérer. Les attributs id_commentaire et date_creation
            seront mis à jour après insertion.

        Retour
        ------
        bool
            True si l'insertion a réussi, False sinon.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO commentaire (id_utilisateur, id_cocktail, texte, note) "
                        "VALUES (%(id_utilisateur)s, %(id_cocktail)s, %(texte)s, %(note)s) "
                        "RETURNING id_commentaire, date_creation;",
                        {
                            "id_utilisateur": commentaire.id_utilisateur,
                            "id_cocktail": commentaire.id_cocktail,
                            "texte": commentaire.texte,
                            "note": commentaire.note,
                        },
                    )
                    result = cursor.fetchone()
                    if result:
                        commentaire.id_commentaire = result["id_commentaire"]
                        commentaire.date_creation = result["date_creation"]
                    return True
        except Exception as e:
            print(f"Erreur création commentaire: {e}")
            return False

    @log
    def trouver_par_cocktail(self, id_cocktail: int) -> list[Commentaire]:
        """
        Récupère les commentaires pour un cocktail spécifique.

        Paramètres
        ----------
        id_cocktail : int
            Identifiant du cocktail.

        Retour
        ------
        List[Commentaire]
            La liste des commentaires pour le cocktail
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT c.*, u.pseudo as pseudo_utilisateur "
                        "FROM commentaire c "
                        "JOIN utilisateur u ON c.id_utilisateur = u.id_utilisateur "
                        "WHERE c.id_cocktail = %(id_cocktail)s "
                        "ORDER BY c.date_creation DESC;",
                        {"id_cocktail": id_cocktail},
                    )
                    results = cursor.fetchall()
                    return [
                        Commentaire(
                            id_commentaire=row["id_commentaire"],
                            id_utilisateur=row["id_utilisateur"],
                            id_cocktail=row["id_cocktail"],
                            texte=row["texte"],
                            note=row["note"],
                            date_creation=row["date_creation"],
                            pseudo_utilisateur=row["pseudo_utilisateur"],
                        )
                        for row in results
                    ]
        except Exception as e:
            print(f"Erreur recherche commentaires: {e}")
            return []

    @log
    def trouver_par_utilisateur_et_cocktail(
        self, id_utilisateur: int, id_cocktail: int | None = None
    ) -> Commentaire | list[Commentaire] | None:
        """
        Récupère le(s) commentaire(s) d'un utilisateur, avec ou sans filtre par cocktail.

        Paramètres
        ----------
        id_utilisateur : int
            Identifiant de l'utilisateur.
        id_cocktail : int | None, optionnel
            Identifiant du cocktail (si None, retourne tous les commentaires de l'utilisateur).

        Retour
        ------
        Commentaire | list[Commentaire] | None
            - Un objet Commentaire si un seul est trouvé (cas avec id_cocktail)
            - Une liste de Commentaire si id_cocktail n’est pas renseigné
            - None si aucun commentaire trouvé
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # recherche par utilisateur + cocktail
                    if id_cocktail is not None:
                        cursor.execute(
                            """
                            SELECT * FROM commentaire
                            WHERE id_utilisateur = %(id_utilisateur)s AND id_cocktail = %(id_cocktail)s;
                            """,
                            {"id_utilisateur": id_utilisateur, "id_cocktail": id_cocktail},
                        )
                        result = cursor.fetchone()
                        if result:
                            return Commentaire(
                                id_commentaire=result["id_commentaire"],
                                id_utilisateur=result["id_utilisateur"],
                                id_cocktail=result["id_cocktail"],
                                texte=result["texte"],
                                note=result["note"],
                                date_creation=result["date_creation"],
                            )
                        return None

                    # recherche uniquement par utilisateur
                    cursor.execute(
                        """
                        SELECT * FROM commentaire
                        WHERE id_utilisateur = %(id_utilisateur)s
                        ORDER BY date_creation DESC;
                        """,
                        {"id_utilisateur": id_utilisateur},
                    )
                    results = cursor.fetchall()
                    if not results:
                        return None

                    return [
                        Commentaire(
                            id_commentaire=row["id_commentaire"],
                            id_utilisateur=row["id_utilisateur"],
                            id_cocktail=row["id_cocktail"],
                            texte=row["texte"],
                            note=row["note"],
                            date_creation=row["date_creation"],
                        )
                        for row in results
                    ]

        except Exception as e:
            print(f"Erreur recherche commentaire: {e}")
            return None

    @log
    def supprimer(self, id_commentaire: int, id_utilisateur: int) -> bool:
        """
        Supprime un commentaire en fonction de son id et de l'utilisateur.

        Paramètres
        ----------
        id_commentaire : int
            Identifiant du commentaire à supprimer.
        id_utilisateur : int
            Identifiant de l'utilisateur propriétaire du commentaire.

        Retour
        ------
        bool
            True si la suppression a été effectuée (au moins une ligne affectée),
            False sinon.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM commentaire "
                        "WHERE id_commentaire = %(id_commentaire)s AND id_utilisateur = %(id_utilisateur)s;",
                        {"id_commentaire": id_commentaire, "id_utilisateur": id_utilisateur},
                    )
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"Erreur suppression commentaire: {e}")
            return False
