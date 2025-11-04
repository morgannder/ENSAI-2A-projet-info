from unittest.mock import MagicMock, patch

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
    """Création de Utilisateur réussie"""
    # GIVEN
    pseudo, mdp, age, langue, est_majeur = "test", "1234", 15, "English", True
    UtilisateurDao().creer_compte = MagicMock(return_value=True)

    # WHEN
    utilisateur = UtilisateurService().creer_utilisateur(
        pseudo, mdp, age, langue, est_majeur
    )

    # THEN
    assert utilisateur.pseudo == pseudo
    assert utilisateur.est_majeur == False


def test_creer_echec():
    """Création de Utilisateur échouée"""
    # GIVEN
    pseudo, mdp, age, langue, est_majeur = "test", "1234", 15, "English", True
    UtilisateurDao().creer_compte = MagicMock(return_value=False)

    # WHEN
    utilisateur = UtilisateurService().creer_utilisateur(
        pseudo, mdp, age, langue, est_majeur
    )

    # THEN
    assert utilisateur is None


def test_pseudo_deja_utilise_oui():
    """Le pseudo est déjà utilisé dans liste_utilisateurs"""
    # GIVEN
    pseudo = "Atty"
    service = UtilisateurService()

    # WHEN - Mock correct de la méthode de l'instance
    with patch.object(UtilisateurDao, "lister_tous", return_value=liste_utilisateurs):
        res = service.pseudo_deja_utilise(pseudo)

    # THEN
    assert res


def test_pseudo_deja_utilise_non():
    """Le pseudo n'est pas utilisé dans liste_utilisateurs"""
    # GIVEN
    pseudo = "NonExistant"
    service = UtilisateurService()

    # WHEN
    with patch.object(UtilisateurDao, "lister_tous", return_value=liste_utilisateurs):
        res = service.pseudo_deja_utilise(pseudo)

    # THEN
    assert not res


def test_se_connecter_oui():
    # GIVEN
    pseudo, mdp = "Atty", "0000Abc"
    service = UtilisateurService()

    # WHEN
    with patch(
        "dao.utilisateur_dao.UtilisateurDao.trouver_par_pseudo",
        return_value=liste_utilisateurs[1],
    ):
        with patch(
            "dao.utilisateur_dao.UtilisateurDao.se_connecter", return_value=True
        ):
            res = service.se_connecter(pseudo, mdp)

    # THEN
    assert res


def test_se_connecter_non():
    """Test de la connexion échouée d'un utilisateur"""
    # GIVEN
    pseudo, mdp = "Atty", "0000Abc"
    service = UtilisateurService()

    # WHEN - Mock pour simuler un échec de connexion
    with patch.object(UtilisateurDao, "trouver_par_pseudo", return_value=None):
        res = service.se_connecter(pseudo, mdp)

    # THEN
    assert res is None


def test_supprimer_compte_oui():
    """Test de la suppression d'un compte utilisateur"""
    # GIVEN
    utilisateur = Utilisateur(
        id_utilisateur=1, pseudo="Atty", mdp="0000Abc", age=25, langue="Italiano"
    )
    service = UtilisateurService()

    # WHEN - Mock pour éviter l'accès à la base
    with patch.object(UtilisateurDao, "supprimer_utilisateur", return_value=True):
        res = service.supprimer_utilisateur(utilisateur)

    # THEN
    assert res


def test_supprimer_compte_non():
    """Test de la suppression échouée d'un compte utilisateur"""
    # GIVEN
    utilisateur = Utilisateur(
        id_utilisateur=1, pseudo="Atty", mdp="0000Abc", age=25, langue="Italiano"
    )
    service = UtilisateurService()

    # WHEN
    with patch.object(UtilisateurDao, "supprimer_utilisateur", return_value=False):
        res = service.supprimer_utilisateur(utilisateur)

    # THEN
    assert not res


def test_verif_mdp_ok():
    """Vérification mot de passe correct"""
    # GIVEN
    mdp_clair = "motdepasse"
    sel = "Français"
    mdp_hash = hash_password(mdp_clair, sel)
    service = UtilisateurService()

    # WHEN
    result = service.verif_mdp(mdp_clair, mdp_hash, sel)

    # THEN
    assert result is True


def test_verif_mdp_non():
    """Vérification mot de passe incorrect"""
    # GIVEN
    mdp_clair = "motdepasse"
    sel = "Français"
    mdp_hash = hash_password("autremdp", sel)
    service = UtilisateurService()

    # WHEN
    result = service.verif_mdp(mdp_clair, mdp_hash, sel)

    # THEN
    assert result is False


# ----------------------------- Tests Fonctionnalitées supplémentaires -----------------------------------#


def test_changer_mdp_identique():
    """Changer mot de passe avec le même mot de passe"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="jp", mdp=hash_password("old", "Français"), age=20, langue="Français"
    )
    service = UtilisateurService()

    # WHEN
    result = service.changer_mdp(utilisateur, "old")

    # THEN
    assert result == "identique"


def test_changer_mdp_success():
    """Changer mot de passe avec succès"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="jp", mdp=hash_password("old", "Français"), age=20, langue="Français"
    )
    nouveau_mdp = "nvMDP"
    service = UtilisateurService()

    # WHEN
    with patch.object(UtilisateurDao, "modifier", return_value=True):
        result = service.changer_mdp(utilisateur, nouveau_mdp)

    # THEN
    assert result == "success"


def test_changer_mdp_echec_dao():
    """Changer mot de passe avec échec DAO"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="jp", mdp=hash_password("old", "Français"), age=20, langue="Français"
    )
    nouveau_mdp = "nvMDP"
    service = UtilisateurService()

    # WHEN
    with patch.object(UtilisateurDao, "modifier", return_value=False):
        result = service.changer_mdp(utilisateur, nouveau_mdp)

    # THEN
    assert result == "echec"


def test_choisir_langue_ok():
    """Changer langue avec succès"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="gg", mdp="abcd", age=18, langue="Italiano", est_majeur=True
    )
    service = UtilisateurService()

    # WHEN
    with patch.object(UtilisateurDao, "modifier", return_value=True):
        res = service.choisir_langue(utilisateur, "English")

    # THEN
    assert res
    assert utilisateur.langue == "English"


def test_choisir_langue_echec():
    """Changer langue avec échec"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="gg", mdp="abcd", age=18, langue="Italiano", est_majeur=True
    )
    service = UtilisateurService()

    # WHEN
    with patch.object(UtilisateurDao, "modifier", return_value=False):
        res = service.choisir_langue(utilisateur, "English")

    # THEN
    assert not res
    assert utilisateur.langue == "English"


def test_changer_pseudo_ok():
    """Changer pseudo avec succès"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="jp", mdp="1234", age=10, langue="Français", est_majeur=False
    )
    service = UtilisateurService()

    # WHEN
    with patch.object(service, "pseudo_deja_utilise", return_value=False):
        with patch.object(UtilisateurDao, "modifier", return_value=True):
            res = service.changer_pseudo(utilisateur, "nouveau")

    # THEN
    assert res
    assert utilisateur.pseudo == "nouveau"


def test_changer_pseudo_deja_pris():
    """Changer pseudo échoue car déjà pris"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="jp", mdp="1234", age=10, langue="Français", est_majeur=False
    )
    service = UtilisateurService()

    # WHEN
    with patch.object(service, "pseudo_deja_utilise", return_value=True):
        res = service.changer_pseudo(utilisateur, "Atty")

    # THEN
    assert not res
    assert utilisateur.pseudo == "jp"


def test_changer_pseudo_echec_dao():
    """Changer pseudo échoue car DAO échoue"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="jp", mdp="1234", age=10, langue="Français", est_majeur=False
    )
    service = UtilisateurService()

    # WHEN
    with patch.object(service, "pseudo_deja_utilise", return_value=False):
        with patch.object(UtilisateurDao, "modifier", return_value=False):
            res = service.changer_pseudo(utilisateur, "nouveau")

    # THEN
    assert not res
    assert utilisateur.pseudo == "nouveau"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
