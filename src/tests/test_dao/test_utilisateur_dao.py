import os
from unittest.mock import patch

import pytest

from business_object.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao
from utils.reset_database import ResetDatabase
from utils.securite import hash_password


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test"""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


# --- TESTS DE LECTURE ----------------------------------------------------


def test_trouver_par_id_existant():
    """Recherche par id d'un utilisateur existant"""
    # GIVEN
    id_utilisateur = 4

    # WHEN
    utilisateur = UtilisateurDao().trouver_par_id(id_utilisateur)

    # THEN
    assert utilisateur is not None
    assert isinstance(utilisateur, Utilisateur)
    assert utilisateur.pseudo == "batricia"


def test_trouver_par_id_non_existant():
    """Recherche par id d'un utilisateur n'existant pas"""
    utilisateur = UtilisateurDao().trouver_par_id(9999)
    assert utilisateur is None


def test_trouver_par_pseudo_existant():
    """Recherche par id d'un utilisateur existant"""
    # GIVEN
    pseudo = "batricia"

    # WHEN
    utilisateur = UtilisateurDao().trouver_par_pseudo(pseudo)

    # THEN
    assert utilisateur is not None
    assert isinstance(utilisateur, Utilisateur)
    assert utilisateur.id_utilisateur == 4


def test_trouver_par_pseudo_non_existant():
    """Recherche par id d'un utilisateur n'existant pas"""
    utilisateur = UtilisateurDao().trouver_par_pseudo("allllo")
    assert utilisateur is None


def test_lister_tous():
    """Liste complète des utilisateurs"""
    utilisateurs = UtilisateurDao().lister_tous()
    assert isinstance(utilisateurs, list)
    assert all(isinstance(u, Utilisateur) for u in utilisateurs)
    assert len(utilisateurs) >= 8


# --- TESTS DE CREATION ----------------------------------------------------


def test_creer_compte_ok():
    """Création de compte réussie"""
    utilisateur = Utilisateur(
        pseudo="gg",
        mdp="motdepasse",
        age=30,
        langue="FRA",
        est_majeur=True,
        date_creation="2025-04-11 16:46:03",
        cocktails_recherches=10,
    )
    creation_ok = UtilisateurDao().creer_compte(utilisateur)
    assert creation_ok
    assert utilisateur.id_utilisateur


def test_creer_compte_ko():
    """Création de compte échouée (valeurs invalides)"""
    utilisateur = Utilisateur(
        pseudo=None,
        mdp=None,
        age="texte",
        langue=123,
        est_majeur="oui",
        date_creation="2025-04-11 16:46:03",
        cocktails_recherches=10,
    )
    creation_ok = UtilisateurDao().creer_compte(utilisateur)
    assert not creation_ok


# --- TESTS DE MODIFICATION ------------------------------------------------


def test_modifier_ko():
    """Modification échouée (id inconnu)"""
    utilisateur = Utilisateur(
        id_utilisateur=9999,
        pseudo="id_inconnu",
        mdp="xxx",
        age=99,
        langue="Deutsch",
        est_majeur=True,
        cocktails_recherches=10,
    )
    modification_ok = UtilisateurDao().modifier(utilisateur)
    assert not modification_ok


def test_modifier_pseudo_deja_existant():
    """Échec de modification si nouveau pseudo déjà utilisé"""
    # GIVEN
    utilisateur = Utilisateur(
        id_utilisateur=5,
        pseudo="batricia",
        mdp="abcd",
        age=24,
        langue="GER",
        est_majeur=True,
        cocktails_recherches=10,
    )

    # WHEN
    modification_ok = UtilisateurDao().modifier(utilisateur)

    # THEN
    assert not modification_ok


# --- TESTS DE SUPPRESSION -------------------------------------------------


def test_supprimer_utilisateur_ok():
    """Suppression d'un utilisateur existant"""
    utilisateur = Utilisateur(
        pseudo="test_supp",
        mdp="motdepasse",
        age=30,
        langue="Français",
        est_majeur=True,
        date_creation="2025-04-11 16:46:03",
        cocktails_recherches=10,
    )
    UtilisateurDao().creer_compte(utilisateur)
    UtilisateurDao().supprimer_inventaire(utilisateur.id_utilisateur)
    suppression_ok = UtilisateurDao().supprimer_utilisateur(utilisateur)
    assert suppression_ok


def test_supprimer_utilisateur_ko():
    """Suppression échouée (id inconnu)"""
    utilisateur = Utilisateur(
        pseudo="inconnu",
        mdp="xxx",
        age=10,
        langue="Français",
        est_majeur=False,
        id_utilisateur=9999,
        cocktails_recherches=10,
    )
    suppression_ok = UtilisateurDao().supprimer_utilisateur(utilisateur)
    assert not suppression_ok


# --- TESTS DE CONNEXION --------------------------------------------------


def test_se_connecter_ok():
    """Connexion réussie"""
    pseudo = "batricia"
    mdp = hash_password("9876", "2025-04-11 16:34:00")

    utilisateur = UtilisateurDao().se_connecter(pseudo, mdp)
    assert isinstance(utilisateur, Utilisateur)
    assert utilisateur.pseudo == pseudo


def test_se_connecter_ko():
    """Test quand une exception se produit pendant la connexion"""
    with patch("dao.utilisateur_dao.DBConnection") as mock_db:
        mock_db.return_value.connection.__enter__.return_value.cursor.return_value.__enter__.return_value.execute.side_effect = Exception(
            "DB error"
        )

        utilisateur = UtilisateurDao().se_connecter("test", "mdp")
        assert utilisateur is None


# --- TESTS FONCTIONNALITÉS SUPPLÉMENTAIRES --------------------------------


def test_ajout_cocktail_recherche_utilisateur_inexistant():
    """Incrémentation échouée pour utilisateur inexistant"""
    # GIVEN
    utilisateur = Utilisateur(
        id_utilisateur=9999,
        pseudo="inexistant",
        mdp="xxx",
        age=30,
        langue="FRA",
        est_majeur=True,
        cocktails_recherches=10,
    )

    # WHEN
    resultat = UtilisateurDao().ajout_cocktail_recherche(utilisateur)

    # THEN
    assert resultat == 0


def test_supprimer_inventaire_id_invalide():
    """Suppression échouée avec ID invalide"""
    # GIVEN
    id_invalide = -1

    # WHEN
    resultat = UtilisateurDao().supprimer_inventaire(id_invalide)

    # THEN
    assert resultat is False


if __name__ == "__main__":
    pytest.main([__file__])
