# src/tests/test_service/test_utilisateur_service.py
from datetime import datetime
from unittest.mock import MagicMock, patch

from business_object.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao
from service.utilisateur_service import UtilisateurService
from utils.securite import hash_password

# date fixe pr les tests
DATE_TEST = datetime(2024, 1, 1, 12, 0, 0)

liste_utilisateurs = [
    Utilisateur(
        pseudo="jp",
        mdp="1234",
        age=10,
        langue="Français",
        est_majeur=False,
        date_creation=DATE_TEST,
    ),
    Utilisateur(pseudo="Atty", mdp="0000Abc", age=25, langue="Italiano", date_creation=DATE_TEST),
    Utilisateur(
        pseudo="gg", mdp="abcd", age=18, langue="Italiano", est_majeur=True, date_creation=DATE_TEST
    ),
]


def test_creer_ok():
    """Création de Utilisateur réussie"""
    # GIVEN
    pseudo, mdp, age, langue, est_majeur = "test", "Mdp1234!", 15, "English", True
    UtilisateurDao().creer_compte = MagicMock(return_value=True)

    # WHEN
    utilisateur = UtilisateurService().creer_utilisateur(pseudo, mdp, age, langue, est_majeur)

    # THEN
    assert utilisateur.pseudo == pseudo
    assert not utilisateur.est_majeur
    assert utilisateur.date_creation is not None  # Vérifie que la date est définie


def test_creer_echec():
    """Création de Utilisateur échouée"""
    # GIVEN
    pseudo, mdp, age, langue, est_majeur = "test", "Mdp1234!", 15, "English", True
    UtilisateurDao().creer_compte = MagicMock(return_value=False)

    # WHEN
    utilisateur = UtilisateurService().creer_utilisateur(pseudo, mdp, age, langue, est_majeur)

    # THEN
    assert utilisateur is None


def test_pseudo_deja_utilise_oui():
    """Le pseudo est déjà utilisé dans liste_utilisateurs"""
    # GIVEN
    pseudo = "Atty"
    service = UtilisateurService()

    # WHEN
    mock_dao = MagicMock()
    mock_dao.lister_tous.return_value = liste_utilisateurs

    with patch("service.utilisateur_service.UtilisateurDao") as MockDao:
        MockDao.return_value = mock_dao
        res = service.pseudo_deja_utilise(pseudo)

    # THEN
    assert res


def test_pseudo_deja_utilise_non():
    """Le pseudo n'est pas utilisé dans liste_utilisateurs"""
    # GIVEN
    pseudo = "NonExistant"
    service = UtilisateurService()

    # WHEN
    mock_dao = MagicMock()
    mock_dao.lister_tous.return_value = liste_utilisateurs

    with patch("service.utilisateur_service.UtilisateurDao") as MockDao:
        MockDao.return_value = mock_dao
        res = service.pseudo_deja_utilise(pseudo)

    # THEN
    assert not res


def test_se_connecter_oui():
    """Test de la connexion d'un utilisateur"""
    # GIVEN
    pseudo, mdp = "Atty", "0000Abc"
    service = UtilisateurService()

    # Mock de trouver_par_pseudo
    mock_utilisateur = Utilisateur(
        id_utilisateur=1,
        pseudo="Atty",
        mdp=hash_password("0000Abc", str(DATE_TEST)),
        age=25,
        langue="Italiano",
        date_creation=DATE_TEST,
    )

    # WHEN
    mock_dao = MagicMock()
    mock_dao.trouver_par_pseudo.return_value = mock_utilisateur
    mock_dao.se_connecter.return_value = mock_utilisateur

    with patch("service.utilisateur_service.UtilisateurDao") as MockDao:
        MockDao.return_value = mock_dao
        res = service.se_connecter(pseudo, mdp)

    # THEN
    assert res is not None
    assert res.pseudo == pseudo


def test_se_connecter_non():
    """Test de la connexion échouée d'un utilisateur"""
    # GIVEN
    pseudo, mdp = "Atty", "0000Abc"
    service = UtilisateurService()

    # WHEN
    mock_dao = MagicMock()
    mock_dao.trouver_par_pseudo.return_value = None

    with patch("service.utilisateur_service.UtilisateurDao") as MockDao:
        MockDao.return_value = mock_dao
        res = service.se_connecter(pseudo, mdp)

    # THEN
    assert res is None


def test_supprimer_compte_oui():
    """Test de la suppression d'un compte utilisateur"""
    # GIVEN
    utilisateur = Utilisateur(
        id_utilisateur=1,
        pseudo="Atty",
        mdp="0000Abc",
        age=25,
        langue="Italiano",
        date_creation=DATE_TEST,
    )
    service = UtilisateurService()

    # WHEN
    mock_dao = MagicMock()
    mock_dao.supprimer_utilisateur.return_value = True

    with patch("service.utilisateur_service.UtilisateurDao") as MockDao:
        MockDao.return_value = mock_dao
        res = service.supprimer_utilisateur(utilisateur)

    # THEN
    assert res


def test_supprimer_compte_non():
    """Test de la suppression échouée d'un compte utilisateur"""
    # GIVEN
    utilisateur = Utilisateur(
        id_utilisateur=1,
        pseudo="Atty",
        mdp="0000Abc",
        age=25,
        langue="Italiano",
        date_creation=DATE_TEST,
    )
    service = UtilisateurService()

    # WHEN
    mock_dao = MagicMock()
    mock_dao.supprimer_utilisateur.return_value = False

    with patch("service.utilisateur_service.UtilisateurDao") as MockDao:
        MockDao.return_value = mock_dao
        res = service.supprimer_utilisateur(utilisateur)

    # THEN
    assert not res


def test_verif_mdp_ok():
    """Vérification mot de passe correct"""
    # GIVEN
    mdp_clair = "motdepasse"
    sel = str(DATE_TEST)  # Utilise la date comme sel
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
    sel = str(DATE_TEST)
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
        pseudo="jp",
        mdp=hash_password("Mdpold1!", str(DATE_TEST)),  # Hash avec la date de création
        age=20,
        langue="Français",
        date_creation=DATE_TEST,  # ⬅️ IMPORTANT : même date pour le sel
    )
    service = UtilisateurService()

    # WHEN
    result = service.changer_mdp(utilisateur, "Mdpold1!")

    # THEN
    assert result == "identique"


def test_changer_mdp_success():
    """Changer mot de passe avec succès"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="jp",
        mdp=hash_password("Mdpold1!", str(DATE_TEST)),
        age=20,
        langue="Français",
        date_creation=DATE_TEST,
    )
    nouveau_mdp = "nvMDP12!"
    service = UtilisateurService()

    # WHEN
    mock_dao = MagicMock()
    mock_dao.modifier.return_value = True

    with patch("service.utilisateur_service.UtilisateurDao") as MockDao:
        MockDao.return_value = mock_dao
        result = service.changer_mdp(utilisateur, nouveau_mdp)

    # THEN
    assert result == "success"
    # Vérifie que le mot de passe a été mis à jour avec le bon sel (date_creation)
    assert utilisateur.mdp == hash_password(nouveau_mdp, str(DATE_TEST))


def test_changer_mdp_echec_dao():
    """Changer mot de passe avec échec DAO"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="jp",
        mdp=hash_password("Mdpold1!", str(DATE_TEST)),
        age=20,
        langue="Français",
        date_creation=DATE_TEST,
    )
    nouveau_mdp = "nvMDP12!"
    service = UtilisateurService()

    # WHEN
    mock_dao = MagicMock()
    mock_dao.modifier.return_value = False

    with patch("service.utilisateur_service.UtilisateurDao") as MockDao:
        MockDao.return_value = mock_dao
        result = service.changer_mdp(utilisateur, nouveau_mdp)

    # THEN
    assert result == "echec"
    # Le mot de passe est quand même mis à jour localement
    assert utilisateur.mdp == hash_password(nouveau_mdp, str(DATE_TEST))


def test_choisir_langue_ok():
    """Changer langue avec succès"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="gg", mdp="abcd", age=18, langue="Italiano", est_majeur=True, date_creation=DATE_TEST
    )
    service = UtilisateurService()

    # WHEN
    mock_dao = MagicMock()
    mock_dao.modifier.return_value = True

    with patch("service.utilisateur_service.UtilisateurDao") as MockDao:
        MockDao.return_value = mock_dao
        res = service.choisir_langue(utilisateur, "English")

    # THEN
    assert res
    assert utilisateur.langue == "English"


def test_choisir_langue_echec():
    """Changer langue avec échec"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="gg", mdp="abcd", age=18, langue="Italiano", est_majeur=True, date_creation=DATE_TEST
    )
    service = UtilisateurService()

    # WHEN
    mock_dao = MagicMock()
    mock_dao.modifier.return_value = False

    with patch("service.utilisateur_service.UtilisateurDao") as MockDao:
        MockDao.return_value = mock_dao
        res = service.choisir_langue(utilisateur, "English")

    # THEN
    assert not res
    assert utilisateur.langue == "English"


def test_changer_pseudo_ok():
    """Changer pseudo avec succès"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="jp",
        mdp="1234",
        age=10,
        langue="Français",
        est_majeur=False,
        date_creation=DATE_TEST,
    )
    service = UtilisateurService()

    # WHEN
    mock_dao = MagicMock()
    mock_dao.modifier.return_value = True

    with patch.object(service, "pseudo_deja_utilise", return_value=False):
        with patch("service.utilisateur_service.UtilisateurDao") as MockDao:
            MockDao.return_value = mock_dao
            res = service.changer_pseudo(utilisateur, "nouveau")

    # THEN
    assert res
    assert utilisateur.pseudo == "nouveau"


def test_changer_pseudo_deja_pris():
    """Changer pseudo échoue car déjà pris"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="jp",
        mdp="1234",
        age=10,
        langue="Français",
        est_majeur=False,
        date_creation=DATE_TEST,
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
        pseudo="jp",
        mdp="1234",
        age=10,
        langue="Français",
        est_majeur=False,
        date_creation=DATE_TEST,
    )
    service = UtilisateurService()

    # WHEN
    mock_dao = MagicMock()
    mock_dao.modifier.return_value = False

    with patch.object(service, "pseudo_deja_utilise", return_value=False):
        with patch("service.utilisateur_service.UtilisateurDao") as MockDao:
            MockDao.return_value = mock_dao
            res = service.changer_pseudo(utilisateur, "nouveau")

    # THEN
    assert not res
    assert utilisateur.pseudo == "nouveau"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
