from business_object.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao
from utils.log_decorator import log
from utils.securite import hash_password


class UtilisateurService:
    """Classe contenant les méthodes de service pour les Utilisateurs"""

    @log
    def creer_utilisateur(self, pseudo, mdp, age, langue) -> Utilisateur:
        """
        Créer un utilisateur et l'ajouter dans la base de données.

        Parameters
        ----------
        pseudo : str
            Pseudo choisi pour l'utilisateur.
        mdp : str
            Mot de passe en clair.
        age : int
            Âge de l'utilisateur.
        langue : str
            Langue de l'utilisateur ("FR", "EN", 'ES").

        Returns
        -------
        Utilisateur
            L'utilisateur créé si succès
            sinon None
        """
        utilisateur = Utilisateur(
            pseudo=pseudo, mdp=hash_password(mdp, pseudo), age=age, langue=langue
        )

        if UtilisateurDao().creer_compte(utilisateur):
            print("Utilisateur créé avec succès.")
            return utilisateur
        else:
            print("Impossible de créer l'utilisateur.")
            return None

    @log
    def se_connecter(self, pseudo, mdp) -> Utilisateur:
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
        Utilisateur
            L'utilisateur trouvé si succès
            sinon None
        """
        pass

    @log
    def deconnecter(self, utilisateur) -> bool:
        """
        Déconnecter un utilisateur de l'app.

        Parameters
        ----------
        utilisateur : Utilisateur
            Utilisateur souhaitant se déconnecter.

        Returns
        -------
        bool
            True si la déconnexion a réussi
            False sinon
        """
        # TODO: Implémenter la déconnexion

    @log
    def supprimer_utilisateur(self, utilisateur) -> bool:
        """
        Supprimer le compte d'un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur
            Utilisateur a supprimer.


        Returns
        -------
        bool
            True si la suppression a réussie
            False sinon
        """
        # TODO: Implémenter la suppression

        pass

    @log
    def pseudo_deja_utilise(self, pseudo: str) -> bool:
        """
        Vérifie si le pseudo est déjà utilisé dans la base de données.

        Parameters
        ----------
        pseudo : str
            Pseudo à vérifier.

        Returns
        -------
        bool
            True si le pseudo existe déjà en BDD, False sinon.
        """
        # TODO: Appeler UtilisateurDao pour lister tous les utilisateurs
        # TODO: Afficher un message à l'utilisateur indiquant si le pseudo est disponible ou non
        utilisateurs = UtilisateurDao().lister_tous()  # méthode a implememter dans le DAO
        return pseudo in [u.pseudo for u in utilisateurs]

    # ----------------------------- Fonctionnalitées supplémentaires -----------------------------------#

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
            True si la suppression a réussie
            False sinon
        """
        # TODO: Implémenter le changement de mot de passe
        pass

    @log
    def choisir_langue(self, utilisateur, langue) -> str:
        """
        Choisir la langue des instructions pour un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur
        langue : str

        Returns
        -------
        str
            Message indiquant le succès ou l'échec.
        """
        # TODO: Implémenter le choix de langue
        pass

    @log
    def est_majeur(self, utilisateur) -> bool:
        """
        Vérifier si l'utilisateur est majeur.

        Parameters
        ----------
        utilisateur : Utilisateur

        Returns
        -------
        est_majeur : bool
            True si majeur
            sinon False
        """
        # TODO: Implémenter la vérification de l'âge

        pass

    @log
    def changer_pseudo(self, utilisateur, nouveau_pseudo) -> bool:
        """
        Changer le pseudo d'un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur
        nouveau_pseudo : str

        Returns
        -------
        bool
            True si succés
            sinon False
        """
        # TODO: Implémenter le changement de pseudo
        pass
