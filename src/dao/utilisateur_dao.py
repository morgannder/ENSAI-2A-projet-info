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
                        "INSERT INTO utilisateur(pseudo, mdp, age, langue) VALUES        "
                        "(%(pseudo)s, %(mdp)s, %(age)s, %(langue)s)                    "
                        "  RETURNING id_utilisateur;                                                ",
                        {
                            "pseudo": utilisateur.pseudo,
                            "mdp": utilisateur.mdp,
                            "age": utilisateur.age,
                            "langue": utilisateur.langue,
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
    def se_connecter(self, pseudo, mdp) -> bool:
        """
        Se connecter avec un pseudo et un mot de passe.

        Parameters
        ----------
        pseudo : str
            Pseudo de l'utilisateur.
        mdp : str
            Mot de passe en clair.

        Returns
        -------
        bool
            True si la connexion a réussi, False sinon.
        """
        # TODO: Appeler utilisateur = UtilisateurDao().se_connecter(pseudo, hash_password(mdp, pseudo)) pour récupérer l'utilisateur
        # TODO: Afficher un message à l'utilisateur selon le résultat
        pass

    @log
    def deconnecter(self, utilisateur) -> bool:
        """
        Déconnecter un utilisateur de l'app.

        Parameters
        ----------
        utilisateur : Utilisateur

        Returns
        -------
        bool
            True si la déconnexion a réussi
            False sinon
        """

        # TODO: Afficher un message à l'utilisateur

        pass

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
        # TODO: Appeler UtilisateurDao().supprimer_compte()
        # TODO: Afficher un message à l'utilisateur

        pass

    @log
    def changer_mdp(self, utilisateur, nouveau_mdp) -> bool:
        """
        Changer le mot de passe d'un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur
        nouveau_mdp : str

        Returns
        -------
        bool
            True si le changement a réussi
            False sinon.
        """
        # TODO: Afficher un message à l'utilisateur

        pass

    @log
    def choisir_langue(self, utilisateur, langue) -> str:
        """
        Choisir la langue des instructions pour un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur
        langue : str
            Langue d'instruction choisie par l'utilisateur

        Returns
        -------
        str
            Langue choisie si succès
            message d'erreur sinon
        """
        # TODO: Afficher un message à l'utilisateur

        pass

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
        # TODO: Appeler UtilisateurDao pour changer le pseudo (DAO-Utilisateur)
        # TODO: Afficher un message à l'utilisateur
        return False
