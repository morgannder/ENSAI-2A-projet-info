from unittest.mock import MagicMock

from service.utilisateur_service import UtilisateurService

from dao.utilisateur_dao import UtilisateurDao

from business_object.utilisateur import Utilisateur

from utils.securite import hash_password


liste_utilisateurs = [
    Utilisateur(pseudo="jp", mdp="1234", age=10, langue="Français", est_majeur=False),
    Utilisateur(pseudo="Atty", mdp="0000Abc", age=25, langue="Italiano"),
    Utilisateur(pseudo="gg", mdp="abcd", age=18, langue="Italiano", est_majeur=True),
]


def test_creer_ok():
    """ "Création de Utilisateur réussie"""

    # GIVEN
    pseudo, mdp, age, langue, est_majeur = "test", "1234", 15, "English", True
    UtilisateurDao().creer_compte = MagicMock(return_value=True)

    # WHEN
    utilisateur = UtilisateurService().creer_utilisateur(pseudo, mdp, age, langue, est_majeur)

    # THEN
    assert utilisateur.pseudo == pseudo
    assert utilisateur.est_majeur == False
    # en soit les utilisateur n'auront pas la main dessus mais tests de la logique



def test_creer_echec():
    """Création de Utilisateur échouée
    (car la méthode UtilisateurDao().creer retourne False)"""

    # GIVEN
    pseudo, mdp, age, langue, est_majeur = "test", "1234", 15, "English", True
    UtilisateurDao().creer_compte = MagicMock(return_value=False)

    # WHEN
    utilisateur = UtilisateurService().creer_utilisateur(pseudo, mdp, age, langue, est_majeur)

    # THEN
    assert utilisateur is None


def test_pseudo_deja_utilise_oui():
    """Le pseudo est déjà utilisé dans liste_utilisateurs"""

    # GIVEN
    pseudo = "Atty"

    # WHEN
    UtilisateurDao().lister_tous = MagicMock(return_value=liste_utilisateurs)
    res = UtilisateurService().pseudo_deja_utilise(pseudo)

    # THEN
    assert res


def test_pseudo_deja_utilise_non():
    """Le pseudo n'est pas utilisé dans liste_utilisateurs"""

    # GIVEN
    pseudo = "Non"

    # WHEN
    UtilisateurDao().lister_tous = MagicMock(return_value=liste_utilisateurs)
    res = UtilisateurService().pseudo_deja_utilise(pseudo)

    # THEN
    assert not res

def test_se_connecter_oui():
    """Test de la connexion d'un utilisateur"""

    # GIVEN
    pseudo, mdp = "Atty", "0000Abc"
    UtilisateurDao().se_connecter = MagicMock(return_value=True)
    # WHEN
    res = UtilisateurService().se_connecter(pseudo, mdp)
    # THEN
    assert res


def test_se_connecter_non():
    """Test de la connexion d'un utilisateur"""

    # GIVEN
    pseudo, mdp = "Atty", "0000Abc"
    UtilisateurDao().se_connecter = MagicMock(return_value=False)
    # WHEN
    res = UtilisateurService().se_connecter(pseudo, mdp)
    # THEN
    assert not res


def test_supprimer_compte_oui():
    """Test de la suppression d'un compte utilisateur"""
    # GIVEN

    UtilisateurDao().supprimer = MagicMock(return_value=True)

    # WHEN
    res = UtilisateurService().supprimer_utilisateur(Utilisateur(pseudo="Atty", mdp="0000Abc", age=25, langue="Italiano"))

    # THEN
    assert res


def test_supprimer_compte_non():
    """Test de la suppression d'un compte utilisateur"""
    # GIVEN
    UtilisateurDao().supprimer = MagicMock(return_value=False)

    # WHEN
    res = UtilisateurService().supprimer_utilisateur(Utilisateur(pseudo="Atty", mdp="0000Abc", age=25, langue="Italiano"))

    # THEN
    assert not res

# ----------------------------- Tests Fonctionnalitées supplémentaires -----------------------------------#

def test_changer_mdp_ok(monkeypatch):
    """Changer le mot de passe avec succès"""
    utilisateur = Utilisateur(pseudo="jp", mdp="old", age=20, langue="Français", est_majeur=True)
    nouveau_mdp = "nvMDP"

    # mock DAO
    UtilisateurDao().modifier = MagicMock(return_value=True)

    res = UtilisateurService().changer_mdp(utilisateur, nouveau_mdp)

    assert res
    assert utilisateur.mdp == hash_password(nouveau_mdp, utilisateur.pseudo)


def test_changer_mdp_echec(monkeypatch):
    """Echec DAO"""
    utilisateur = Utilisateur(pseudo="jp", mdp="old", age=20, langue="Français", est_majeur=True)
    nouveau_mdp = "nvMDP"

    UtilisateurDao().modifier = MagicMock(return_value=False)

    res = UtilisateurService().changer_mdp(utilisateur, nouveau_mdp)

    assert not res
    assert utilisateur.mdp == hash_password(nouveau_mdp, utilisateur.pseudo)

def test_choisir_langue_ok():
    """Choisir la langue avec succès"""
    utilisateur = Utilisateur(pseudo="gg", mdp="abcd", age=18, langue="Italiano", est_majeur=True)
    UtilisateurDao().modifier = MagicMock(return_value=True)

    res = UtilisateurService().choisir_langue(utilisateur, "English")

    assert res
    assert utilisateur.langue == "English"


def test_choisir_langue_echec():
    """Echec de la DAO"""
    utilisateur = Utilisateur(pseudo="gg", mdp="abcd", age=18, langue="Italiano", est_majeur=True)
    UtilisateurDao().modifier = MagicMock(return_value=False)

    res = UtilisateurService().choisir_langue(utilisateur, "English")

    assert not res
    assert utilisateur.langue == "English"  # valeur quand même changée avant la tentative


def test_changer_pseudo_ok(monkeypatch):
    """Changer le pseudo avec succès"""
    utilisateur = Utilisateur(pseudo="jp", mdp="1234", age=10, langue="Français", est_majeur=False)

    # Mock : pseudo non utilisé + DAO réussit
    UtilisateurService.pseudo_deja_utilise = MagicMock(return_value=False)
    UtilisateurDao().modifier = MagicMock(return_value=True)

    res = UtilisateurService().changer_pseudo(utilisateur, "nouveau")

    assert res
    assert utilisateur.pseudo == "nouveau"


def test_changer_pseudo_deja_pris():
    """Changer le pseudo échoue car déjà utilisé"""
    utilisateur = Utilisateur(pseudo="jp", mdp="1234", age=10, langue="Français", est_majeur=False)

    UtilisateurService.pseudo_deja_utilise = MagicMock(return_value=True)
    UtilisateurDao().modifier = MagicMock(return_value=True)  # ne doit pas être appelé

    res = UtilisateurService().changer_pseudo(utilisateur, "Atty")

    assert not res
    assert utilisateur.pseudo == "jp"  # inchangé


def test_changer_pseudo_echec_dao():
    """Changer le pseudo échoue car DAO renvoie False"""
    utilisateur = Utilisateur(pseudo="jp", mdp="1234", age=10, langue="Français", est_majeur=False)

    UtilisateurService.pseudo_deja_utilise = MagicMock(return_value=False)
    UtilisateurDao().modifier = MagicMock(return_value=False)

    res = UtilisateurService().changer_pseudo(utilisateur, "nouveau")

    assert not res
    assert utilisateur.pseudo == "nouveau"  # modifié avant le retour False


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
