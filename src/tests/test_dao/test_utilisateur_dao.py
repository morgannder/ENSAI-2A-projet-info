import os
import pytest

from unittest.mock import patch

from utils.reset_database import ResetDatabase
from utils.securite import hash_password

from dao.utilisateur_dao import UtilisateurDao

from business_object.utilisateur import Utilisateur


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
    id_utilisateur = 4  # 'batricia' dans le pop_db_test

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
        pseudo="gg", mdp="motdepasse", age=30, langue="Français", est_majeur=True
    )
    creation_ok = UtilisateurDao().creer_compte(utilisateur)
    assert creation_ok
    assert utilisateur.id_utilisateur


def test_creer_compte_ko():
    """Création de compte échouée (valeurs invalides)"""
    utilisateur = Utilisateur(
        pseudo=None, mdp=None, age="texte", langue=123, est_majeur="oui"
    )
    creation_ok = UtilisateurDao().creer_compte(utilisateur)
    assert not creation_ok


# --- TESTS DE MODIFICATION ------------------------------------------------


def test_modifier_ok():
    """Modification réussie"""
    utilisateur = Utilisateur(
        id_utilisateur=5,  # Gilbert existe
        pseudo="Gilbert_modif",
        mdp="abcd",
        age=24,
        langue="Deutsch",
        est_majeur=True,
    )
    modification_ok = UtilisateurDao().modifier(utilisateur)
    assert modification_ok


def test_modifier_ko():
    """Modification échouée (id inconnu)"""
    utilisateur = Utilisateur(
        id_utilisateur=9999,
        pseudo="id_inconnu",
        mdp="xxx",
        age=99,
        langue="Deutsch",
        est_majeur=True,
    )
    modification_ok = UtilisateurDao().modifier(utilisateur)
    assert not modification_ok


# --- TESTS DE SUPPRESSION -------------------------------------------------


def test_supprimer_utilisateur_ok():
    """Suppression d'un utilisateur existant"""
    utilisateur = Utilisateur(
        pseudo="test_supp", mdp="motdepasse", age=30, langue="Français", est_majeur=True
    )
    UtilisateurDao().creer_compte(utilisateur)
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
    )
    suppression_ok = UtilisateurDao().supprimer_utilisateur(utilisateur)
    assert not suppression_ok


# --- TESTS DE CONNEXION --------------------------------------------------


def test_se_connecter_ok():
    """Connexion réussie"""
    pseudo = "batricia"
    mdp = "9876"  # non hashé dans la base

    utilisateur = UtilisateurDao().se_connecter(pseudo, mdp)
    assert isinstance(utilisateur, Utilisateur)
    assert utilisateur.pseudo == pseudo


def test_se_connecter_ko():
    """Connexion échouée"""
    pseudo = "batricia"
    mdp = "mauvaismdp"

    utilisateur = UtilisateurDao().se_connecter(pseudo, mdp)
    assert utilisateur is None


if __name__ == "__main__":
    pytest.main([__file__])
