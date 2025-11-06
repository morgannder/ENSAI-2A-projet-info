import logging

from business_object.utilisateur import Utilisateur
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class UtilisateurDao(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Utlilisateurs de la base de données"""

    @log
    def creer_compte(self, utilisateur: Utilisateur) -> bool:
        """Creation d'un Utilisateur dans la base de données

        Parameters
        ----------
        utilisateur : Utilisateur

        Returns
        -------
        created : bool
            True si la création est un succès
            False sinon
        """

        res = None
        created = False
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO utilisateur(pseudo, mdp, age, langue, est_majeur, date_creation, cocktails_realises) VALUES        "
                        "(%(pseudo)s, %(mdp)s, %(age)s, %(langue)s, %(est_majeur)s, %(date_creation)s, %(cocktails_realises)s)                    "
                        "  RETURNING id_utilisateur;                                                ",
                        {
                            "pseudo": utilisateur.pseudo,
                            "mdp": utilisateur.mdp,
                            "age": utilisateur.age,
                            "langue": utilisateur.langue,
                            "est_majeur": utilisateur.est_majeur,
                            "date_creation": utilisateur.date_creation,
                            "cocktails_realises": utilisateur.cocktails_realises,
                        },
                    )
                    res = cursor.fetchone()
                    # on ajoute l'au par défaut dans l'inventaire
                    if res:
                        id_utilisateur = res["id_utilisateur"]
                        utilisateur.id_utilisateur = id_utilisateur
                        created = True
                        with connection.cursor() as cursor:
                            cursor.execute(
                                """
                                INSERT INTO inventaire_ingredient (id_utilisateur, id_ingredient)
                                VALUES (%(id_utilisateur)s, %(id_ingredient)s)
                                ON CONFLICT DO NOTHING;
                                """,
                                {
                                    "id_utilisateur": utilisateur.id_utilisateur,
                                    "id_ingredient": 408,
                                },
                            )
        except Exception as e:
            logging.info(e)

        return created

    @log
    def se_connecter(self, pseudo: str, mdp: str) -> Utilisateur:
        """
        Se connecter avec un pseudo et un mot de passe.

        Parameters
        ----------
        pseudo : str
            Pseudo de l'utilisateur.
        mdp : str
            Mot de passe de l'utilisateur

        Returns
        -------
        Utilisateur
            Renvoie l'utilisateur qui se connecte
        """
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                           "
                        "  FROM utilisateur                      "
                        " WHERE pseudo = %(pseudo)s         "
                        "   AND mdp = %(mdp)s;              ",
                        {"pseudo": pseudo, "mdp": mdp},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)

        utilisateur = None

        if res:
            utilisateur = Utilisateur(
                pseudo=res["pseudo"],
                mdp=res["mdp"],
                age=res["age"],
                langue=res["langue"],
                est_majeur=res["est_majeur"],
                date_creation=res["date_creation"],
                id_utilisateur=res["id_utilisateur"],
                cocktails_realises=res["cocktails_realises"],
            )

        return utilisateur

    @log
    def supprimer_utilisateur(self, utilisateur: Utilisateur) -> bool:
        """
        Supprimer le compte d'un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur

        Returns
        -------
        bool
            True si la suppression est un succès
            False sinon
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM utilisateur                  "
                        " WHERE id_utilisateur=%(id_utilisateur)s      ",
                        {"id_utilisateur": utilisateur.id_utilisateur},
                    )
                    res = cursor.rowcount
        except Exception:
            logging.exception("Erreur lors de la création de compte")
            raise

        return res > 0

    def supprimer_inventaire(self, id_utilisateur: int) -> bool:
        """Supprime l'inventaire de l'utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur

        Returns
        -------
        deleted : bool
            True si la suppression est un succès
            False sinon
        """
        if not isinstance(id_utilisateur, int) or id_utilisateur <= 0:
            return False

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM inventaire_ingredient
                        WHERE id_utilisateur = %(idu)s;
                        """,
                        {"idu": id_utilisateur},
                    )
                    deleted = cursor.rowcount
        except Exception as e:
            logging.exception(
                "Erreur lors de la suppression de l'inventaire de l'utilisateur: %s",
                e,
            )
            return False

        return deleted > 0

    @log
    def trouver_par_id(self, id_utilisateur: int) -> Utilisateur:
        """trouver un utilisateur grace à son id

        Parameters
        ----------
        id_utilisateur : int
            numéro id de l'utilisateur que l'on souhaite trouver

        Returns
        -------
        utilisateur : Utilisateur
            renvoie l'utilisateur que l'on cherche par id
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                           "
                        "  FROM utilisateur                      "
                        " WHERE id_utilisateur = %(id_utilisateur)s;  ",
                        {"id_utilisateur": id_utilisateur},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        utilisateur = None
        if res:
            utilisateur = Utilisateur(
                pseudo=res["pseudo"],
                mdp=res["mdp"],
                age=res["age"],
                langue=res["langue"],
                est_majeur=res["est_majeur"],
                date_creation=res["date_creation"],
                id_utilisateur=res["id_utilisateur"],
                cocktails_realises=res["cocktails_realises"],
            )

        return utilisateur

    @log
    def trouver_par_pseudo(self, pseudo: str) -> Utilisateur:
        """trouver un utilisateur grace à son pseudo

        Parameters
        ----------
        pseudo : str
            pseudo de l'utilisateur que l'on souhaite trouver

        Returns
        -------
        utilisateur : Utilisateur
            renvoie l'utilisateur que l'on cherche
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                           "
                        "  FROM utilisateur                      "
                        " WHERE pseudo = %(pseudo)s;  ",
                        {"pseudo": pseudo},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)
            raise

        utilisateur = None
        if res:
            utilisateur = Utilisateur(
                pseudo=res["pseudo"],
                mdp=res["mdp"],
                age=res["age"],
                langue=res["langue"],
                est_majeur=res["est_majeur"],
                date_creation=res["date_creation"],
                id_utilisateur=res["id_utilisateur"],
                cocktails_realises=res["cocktails_realises"],
            )

        return utilisateur

    @log
    def lister_tous(self) -> list[Utilisateur]:
        """lister tous les utilisateurs

        Parameters
        ----------
        None

        Returns
        -------
        liste_utilisateurs : list[Joueur]
            renvoie la liste de tous les utilisateurs dans la base de données
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                              "
                        "  FROM utilisateur;                        "
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logging.info(e)
            raise

        liste_utilisateurs = []

        if res:
            for row in res:
                utilisateur = Utilisateur(
                    pseudo=row["pseudo"],
                    mdp=row["mdp"],
                    age=row["age"],
                    langue=row["langue"],
                    est_majeur=row["est_majeur"],
                    date_creation=row["date_creation"],
                    id_utilisateur=row["id_utilisateur"],
                    cocktails_realises=row["cocktails_realises"],
                )

                liste_utilisateurs.append(utilisateur)

        return liste_utilisateurs

    # ----------------------------- Fonctionnalitées supplémentaires -----------------------------------

    ## OPTION 1 : fonction commune pour la mmodif des elements
    @log
    def modifier(self, utilisateur: Utilisateur) -> bool:
        """
        Modification d'un utilisateur dans la base de données

        Parameters
        ----------
        utilisateur : Utilisateur

        Returns
        -------
        bool
            True si la modification est un succès
            False sinon
        """

        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE utilisateur
                        SET pseudo = %(pseudo)s,
                            mdp = %(mdp)s,
                            age = %(age)s,
                            langue = %(langue)s,
                            est_majeur = %(est_majeur)s,
                            cocktails_realises = %(cocktails_realises)s
                        WHERE id_utilisateur = %(id_utilisateur)s;
                        """,
                        {
                            "pseudo": utilisateur.pseudo,
                            "mdp": utilisateur.mdp,
                            "age": utilisateur.age,
                            "langue": utilisateur.langue,
                            "est_majeur": utilisateur.est_majeur,
                            "id_utilisateur": utilisateur.id_utilisateur,
                            "cocktails_realises": utilisateur.cocktails_realises,
                        },
                    )
                    res = cursor.rowcount  # renvoie le nombre de lignes affectées
        except Exception as e:
            logging.info(e)
        return res == 1
