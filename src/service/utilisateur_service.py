from business_object.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao
from utils.log_decorator import log
from utils.securite import hash_password
from datetime import datetime



class UtilisateurService:
    """Classe contenant les méthodes de service pour les Utilisateurs"""

    @log
    def creer_utilisateur(self, pseudo, mdp, age, langue, est_majeur) -> Utilisateur:
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
        if age >= 18:
            est_majeur = True
        else:
            est_majeur = False

        date_creation = datetime.now()

        # hashage du mdp avec le sel (le pseudo qui est unique pr chaque utilisateur)
        utilisateur = Utilisateur(
            pseudo=pseudo,
            mdp=hash_password(mdp, str(date_creation)),
            age=age,
            langue=langue,
            est_majeur=est_majeur,
            date_creation=date_creation,
        )

        if UtilisateurDao().creer_compte(utilisateur):
            return utilisateur
        else:
            return None

    @log
    def trouver_par_pseudo(self, id_utilisateur) -> Utilisateur:
        """Trouver un utilisateur à partir de son pseudo"""
        return UtilisateurDao().trouver_par_pseudo(id_utilisateur)

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
        utilisateur = self.trouver_par_pseudo(pseudo)
        if not utilisateur:
            return None
        mdp = hash_password(mdp, str(utilisateur.date_creation)),
        return UtilisateurDao().se_connecter(pseudo, mdp)

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
        return UtilisateurDao().supprimer_utilisateur(utilisateur)

    @log
    def pseudo_deja_utilise(self, pseudo: str, utilisateur_id=None) -> bool:
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
        utilisateurs = UtilisateurDao().lister_tous()
        return pseudo in [u.pseudo for u in utilisateurs]

    @log
    def trouver_par_id(self, id_utilisateur) -> Utilisateur:
        """Trouver un utilisateur à partir de son id"""
        return UtilisateurDao().trouver_par_id(id_utilisateur)

    # ----------------------------- Fonctionnalitées supplémentaires -----------------------------------#
    @log
    def verif_mdp(self, mdp_clair: str, mdp_hash: str, sel: str = "") -> bool:
        """Vérifie si le mot de passe en clair correspond au hash stocké"""
        return hash_password(mdp_clair, sel) == mdp_hash

    @log
    def changer_mdp(self, utilisateur, nouveau_mdp) -> str:
        """
        Changer le mot de passe d'un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur
        nouveau_mdp : str

        Returns
        -------
        str
            identique si le mdp entré est le même que l'ancien
            success si changement réussi
            echec sinon
        """
        if self.verif_mdp(nouveau_mdp, utilisateur.mdp, sel=str(utilisateur.date_creation)):
            return "identique"
        utilisateur.mdp = hash_password(nouveau_mdp, str(utilisateur.date_creation))

        if UtilisateurDao().modifier(utilisateur):
            return "success"
        else:
            return "echec"

    @log
    def choisir_langue(self, utilisateur, langue) -> bool:
        """
        Choisir la langue des instructions pour un utilisateur.

        Parameters
        ----------
        utilisateur : Utilisateur
        langue : str

        Returns
        -------
        bool
            True si succés
            sinon False
        """
        utilisateur.langue = langue
        return UtilisateurDao().modifier(utilisateur)

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
        # verification de la validité du pseudo
        if self.pseudo_deja_utilise(nouveau_pseudo):
            return False
        utilisateur.pseudo = nouveau_pseudo
        return UtilisateurDao().modifier(utilisateur)

        # ou alors avec les ofncitons specifiques
