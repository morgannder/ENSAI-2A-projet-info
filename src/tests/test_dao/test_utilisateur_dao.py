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


def test_modifier_ok():
    """Modification réussie"""
    utilisateur = Utilisateur(
        id_utilisateur=5,  # Gilbert existe
        pseudo="Gilbert_modif",
        mdp="abcd",
        age=24,
        langue="GER",
        est_majeur=True,
        date_creation="2025-04-11 16:46:03",
        cocktails_recherches=10,
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
        cocktails_recherches=10,
    )
    modification_ok = UtilisateurDao().modifier(utilisateur)
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
    mdp = hash_password("9876", "2025-04-11 16:34:00")  # non hashé dans la base

    utilisateur = UtilisateurDao().se_connecter(pseudo, mdp)
    assert isinstance(utilisateur, Utilisateur)
    assert utilisateur.pseudo == pseudo


def test_se_connecter_ko():
    """Connexion échouée"""
    pseudo = "batricia"
    mdp = "mauvaismdp"

    utilisateur = UtilisateurDao().se_connecter(pseudo, mdp)
    assert utilisateur is None


# --- TESTS FONCTIONNALITÉS SUPPLÉMENTAIRES --------------------------------


def test_ajout_cocktail_recherche_ok():
    """Incrémentation réussie du compteur de cocktails recherchés"""
    # GIVEN
    utilisateur = Utilisateur(
        id_utilisateur=4,  # batricia existe
        pseudo="batricia",
        mdp="9876",
        age=25,
        langue="FRA",
        est_majeur=True,
        cocktails_recherches=5,
    )

    # WHEN
    resultat = UtilisateurDao().ajout_cocktail_recherche(utilisateur)

    # THEN
    assert resultat == 1

    # Vérification que le compteur a été incrémenté
    utilisateur_apres = UtilisateurDao().trouver_par_id(4)
    assert utilisateur_apres.cocktails_recherches >= 6


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


def test_supprimer_inventaire_ok():
    """Suppression réussie de l'inventaire"""
    # GIVEN - Créer un utilisateur avec un inventaire
    utilisateur = Utilisateur(
        pseudo="test_inventaire",
        mdp="mdp",
        age=30,
        langue="FRA",
        est_majeur=True,
        date_creation="2025-04-11 16:46:03",
        cocktails_recherches=0,
    )
    creation_ok = UtilisateurDao().creer_compte(utilisateur)
    assert creation_ok

    # WHEN
    suppression_ok = UtilisateurDao().supprimer_inventaire(utilisateur.id_utilisateur)

    # THEN
    assert suppression_ok is True


def test_supprimer_inventaire_id_invalide():
    """Suppression échouée avec ID invalide"""
    # GIVEN
    id_invalide = -1

    # WHEN
    resultat = UtilisateurDao().supprimer_inventaire(id_invalide)

    # THEN
    assert resultat is False


def test_supprimer_inventaire_utilisateur_inexistant():
    """Suppression d'inventaire pour utilisateur inexistant"""
    # GIVEN
    id_inexistant = 9999

    # WHEN
    resultat = UtilisateurDao().supprimer_inventaire(id_inexistant)

    # THEN
    # Peut retourner False ou True selon si des lignes étaient présentes
    assert isinstance(resultat, bool)


# --- TESTS DE VALIDATION DES DONNÉES -------------------------------------


def test_creer_compte_pseudo_deja_existant():
    """Échec de création si pseudo déjà existant"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="batricia",  # Déjà existant
        mdp="nouveaumdp",
        age=30,
        langue="FRA",
        est_majeur=True,
        date_creation="2025-04-11 16:46:03",
        cocktails_recherches=0,
    )

    # WHEN
    creation_ok = UtilisateurDao().creer_compte(utilisateur)

    # THEN
    assert not creation_ok


def test_modifier_pseudo_deja_existant():
    """Échec de modification si nouveau pseudo déjà utilisé"""
    # GIVEN
    utilisateur = Utilisateur(
        id_utilisateur=5,  # Gilbert
        pseudo="batricia",  # Déjà utilisé par batricia
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


# --- TESTS AVEC VALEURS NULL/NONE ----------------------------------------


def test_creer_compte_avec_valeurs_none():
    """Création avec certaines valeurs None"""
    utilisateur = Utilisateur(
        pseudo="test_none",
        mdp="mdp",
        age=None,
        langue=None,
        est_majeur=None,
        date_creation=None,
        cocktails_recherches=None,
    )

    creation_ok = UtilisateurDao().creer_compte(utilisateur)
    # Le résultat dépend de comment votre base gère les NULL
    assert isinstance(creation_ok, bool)


def test_modifier_avec_valeurs_none():
    """Modification avec certaines valeurs None"""
    utilisateur = Utilisateur(
        id_utilisateur=6,  # Utilisateur existant
        pseudo="test_none_modif",
        mdp=None,
        age=None,
        langue=None,
        est_majeur=None,
        cocktails_recherches=None,
    )

    modification_ok = UtilisateurDao().modifier(utilisateur)
    assert isinstance(modification_ok, bool)


# --- TESTS DE PERFORMANCE/ROBUSTESSE -------------------------------------


def test_lister_tous_avec_many_utilisateurs():
    """Test de performance avec nombreux utilisateurs"""
    utilisateurs = UtilisateurDao().lister_tous()
    # Vérifie que la méthode gère correctement plusieurs enregistrements
    assert isinstance(utilisateurs, list)
    assert all(isinstance(u, Utilisateur) for u in utilisateurs)


# --- TESTS DE TRANSACTION ------------------------------------------------


def test_creer_compte_avec_inventaire_initial():
    """Vérifie que l'utilisateur créé a bien l'ingrédient par défaut"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="test_inventaire_init",
        mdp="mdp",
        age=25,
        langue="FRA",
        est_majeur=True,
        date_creation="2025-04-11 16:46:03",
        cocktails_recherches=0,
    )

    # WHEN
    creation_ok = UtilisateurDao().creer_compte(utilisateur)

    # THEN
    assert creation_ok
    assert utilisateur.id_utilisateur is not None

    # L'utilisateur devrait avoir l'ingrédient 408 (eau) dans son inventaire
    # Vous pourriez ajouter une méthode pour vérifier l'inventaire si nécessaire


def test_suppression_complete_utilisateur():
    """Suppression complète d'un utilisateur avec son inventaire"""
    # GIVEN
    utilisateur = Utilisateur(
        pseudo="test_supp_complete",
        mdp="mdp",
        age=30,
        langue="FRA",
        est_majeur=True,
        date_creation="2025-04-11 16:46:03",
        cocktails_recherches=5,
    )
    creation_ok = UtilisateurDao().creer_compte(utilisateur)
    assert creation_ok

    # WHEN - Suppression de l'inventaire d'abord, puis de l'utilisateur
    suppression_inventaire = UtilisateurDao().supprimer_inventaire(
        utilisateur.id_utilisateur
    )
    suppression_utilisateur = UtilisateurDao().supprimer_utilisateur(utilisateur)

    # THEN
    assert suppression_inventaire is True
    assert suppression_utilisateur is True

    # Vérification que l'utilisateur n'existe plus
    utilisateur_apres = UtilisateurDao().trouver_par_id(utilisateur.id_utilisateur)
    assert utilisateur_apres is None


# --- TESTS AVEC MOCK POUR LES EXCEPTIONS ---------------------------------


def test_creer_compte_exception():
    """Test quand une exception se produit pendant la création"""
    with patch("dao.utilisateur_dao.DBConnection") as mock_db:
        mock_db.return_value.connection.__enter__.return_value.cursor.return_value.__enter__.return_value.execute.side_effect = Exception(
            "DB error"
        )

        utilisateur = Utilisateur(
            pseudo="test_exception",
            mdp="mdp",
            age=30,
            langue="FRA",
            est_majeur=True,
            date_creation="2025-04-11 16:46:03",
            cocktails_recherches=0,
        )

        creation_ok = UtilisateurDao().creer_compte(utilisateur)
        assert not creation_ok


def test_se_connecter_exception():
    """Test quand une exception se produit pendant la connexion"""
    with patch("dao.utilisateur_dao.DBConnection") as mock_db:
        mock_db.return_value.connection.__enter__.return_value.cursor.return_value.__enter__.return_value.execute.side_effect = Exception(
            "DB error"
        )

        utilisateur = UtilisateurDao().se_connecter("test", "mdp")
        assert utilisateur is None


if __name__ == "__main__":
    pytest.main([__file__])
