import logging

from business_object.utilisateur import Utilisateur
from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class UtilisateurDao(metaclass=Singleton):
    """Classe contenant les méthodes pour accéder aux Utlilisateurs de la base de données"""

    @log
    def creer_compte(self, utilisateur) -> bool:
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

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO utilisateur(pseudo, mdp, age, langue, est_majeur) VALUES        "
                        "(%(pseudo)s, %(mdp)s, %(age)s, %(langue)s, %(est_majeur)s)                    "
                        "  RETURNING id_utilisateur;                                                ",
                        {
                            "pseudo": utilisateur.pseudo,
                            "mdp": utilisateur.mdp,
                            "age": utilisateur.age,
                            "langue": utilisateur.langue,
                            "est_majeur": utilisateur.est_majeur,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)

        created = False
        if res:
            utilisateur.id_utilisateur = res["id_utilisateur"]
            created = True

        return created

    @log
    def se_connecter(self, pseudo, mdp) -> Utilisateur:
        """
        Se connecter avec un pseudo et un mot de passe.

        Parameters
        ----------
        pseudo : str
            Pseudo de l'utilisateur.
        mdp : str
            Mot de passe hashé.

        Returns
        -------
        Utilisateur
            Renvoie l'utilisateur que l'on souhaite chercher
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
                id_utilisateur=res["id_utilisateur"]
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
            True si la suppression a réussi
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
        except Exception as e:
            logging.exception("Erreur lors de la création de compte")
            raise

        return res > 0


    @log
    def trouver_par_id(self, id_utilisateur) -> Utilisateur:
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
                id_utilisateur=res["id_utilisateur"],
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
                    id_utilisateur=row["id_utilisateur"],
                )

                liste_utilisateurs.append(utilisateur)

        return liste_utilisateurs


# ----------------------------- Fonctionnalitées supplémentaires -----------------------------------#

    ## OPTION 1 : fonction commune pour la mmodif des elements
    @log
    def modifier(self, utilisateur) -> bool:
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
                            est_majeur = %(est_majeur)s
                        WHERE id_utilisateur = %(id_utilisateur)s;
                        """,
                        {
                            "pseudo": utilisateur.pseudo,
                            "mdp": utilisateur.mdp,
                            "age": utilisateur.age,
                            "langue": utilisateur.langue,
                            "est_majeur": utilisateur.est_majeur,
                            "id_utilisateur": utilisateur.id_utilisateur,
                        },
                    )
                    res = cursor.rowcount  # renvoie le nombre de lignes affectées
        except Exception as e:
            logging.info(e)
        return res == 1

    ## OPTION 2 : fonctions séparées pour la mmodif des elements

    @log
    def changer_mdp(self, utilisateur, nouveau_mdp) -> bool:
        """
        Changer le mot de passe d'un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur
        nouveau_mdp hashé : str

        Returns
        -------
        bool
            True si le changement a réussi
            False sinon.
        """
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE utilisateur SET mdp = %(mdp)s WHERE id_utilisateur = %(id_utilisateur)s;",
                        {
                            "mdp": nouveau_mdp,
                            "id_utilisateur": utilisateur.id_utilisateur
                        }
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
        return res == 1


    @log
    def choisir_langue(self, utilisateur, langue) -> bool:
        """
        Choisir la langue des instructions pour un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur
        langue : str
            Langue d'instruction choisie par l'utilisateur

        Returns
        -------
        bool
            True si le changement a réussi, False sinon.
        """
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE utilisateur SET langue = %(langue)s WHERE id_utilisateur = %(id_utilisateur)s;",
                        {
                            "langue": nouvelle_langue,
                            "id_utilisateur": utilisateur.id_utilisateur
                        }
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
        return res == 1

    @log
    def changer_pseudo(self, utilisateur: Utilisateur, nouveau_pseudo: str) -> bool:
        """
        Changer le pseudo d'un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur
        nouveau_pseudo : str

        Returns
        -------
        bool
            True si le changement a réussi, False sinon.
        """
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE utilisateur SET pseudo = %(pseudo)s WHERE id_utilisateur = %(id_utilisateur)s;",
                        {
                            "pseudo": nouveau_pseudo,
                            "id_utilisateur": utilisateur.id_utilisateur
                        }
                    )
                    res = cursor.rowcount
        except Exception as e:
            logging.info(e)
        return res == 1
