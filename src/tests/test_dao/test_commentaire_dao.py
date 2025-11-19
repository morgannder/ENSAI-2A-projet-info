import os
from unittest.mock import patch

import pytest

from business_object.commentaire import Commentaire
from dao.commentaire_dao import CommentaireDao
from utils.reset_database import ResetDatabase


# ----------------------------------------------------------------------
# Initialisation : on utilise le schéma de test et on repop la base
# ----------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation de la base de test (schéma projet_test_dao)."""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


# ----------------------------------------------------------------------
# Tests creer
# ----------------------------------------------------------------------
def test_creer_commentaire_succes():
    """Création d'un commentaire valide -> id_commentaire rempli."""
    com = Commentaire(id_utilisateur=1, id_cocktail=0, texte="Test création", note=4)
    ok = CommentaireDao().creer(com)
    assert ok is True
    assert com.id_commentaire is not None
    assert com.date_creation is not None


def test_creer_commentaire_texte_vide():
    """Commentaire avec texte vide -> retourne False."""
    com = Commentaire(id_utilisateur=1, id_cocktail=0, texte="   ", note=3)
    ok = CommentaireDao().creer(com)
    assert ok is False


def test_creer_commentaire_note_invalide():
    """Commentaire avec note hors limites -> retourne False."""
    com = Commentaire(id_utilisateur=1, id_cocktail=0, texte="Test", note=0)
    ok = CommentaireDao().creer(com)
    assert ok is False


# ----------------------------------------------------------------------
# Tests trouver_par_cocktail
# ----------------------------------------------------------------------
def test_trouver_par_cocktail_existant():
    """Récupération de commentaires pour un cocktail existant."""
    id_cocktail = 0  # Mojito dans la base test
    commentaires = CommentaireDao().trouver_par_cocktail(id_cocktail)
    assert isinstance(commentaires, list)
    assert len(commentaires) > 0
    # Vérifie que les objets sont bien de type Commentaire
    assert all(isinstance(c, Commentaire) for c in commentaires)


def test_trouver_par_cocktail_aucun_resultat():
    """Cocktail inexistant ou sans commentaire -> liste vide"""
    commentaires = CommentaireDao().trouver_par_cocktail(99999)
    assert commentaires == []


# ----------------------------------------------------------------------
# Tests trouver_par_utilisateur_et_cocktail
# ----------------------------------------------------------------------
def test_trouver_par_utilisateur_et_cocktail_existant():
    """Récupère un commentaire existant."""
    com = CommentaireDao().trouver_par_utilisateur_et_cocktail(3, 0)
    assert com is not None
    assert com.id_utilisateur == 3
    assert com.id_cocktail == 0


def test_trouver_par_utilisateur_et_cocktail_inexistant():
    """Commentaire inexistant -> None"""
    com = CommentaireDao().trouver_par_utilisateur_et_cocktail(999, 999)
    assert com is None


# ----------------------------------------------------------------------
# Tests supprimer
# ----------------------------------------------------------------------
def test_supprimer_commentaire_existant():
    """Suppression d'un commentaire existant -> True"""
    # Créer un commentaire pour tester la suppression
    com = Commentaire(id_utilisateur=1, id_cocktail=2, texte="À supprimer", note=3)
    CommentaireDao().creer(com)
    assert com.id_commentaire is not None

    ok = CommentaireDao().supprimer(com.id_commentaire, com.id_utilisateur)
    assert ok is True

    # Vérifie qu'il n'existe plus
    com_check = CommentaireDao().trouver_par_utilisateur_et_cocktail(
        com.id_utilisateur, com.id_cocktail
    )
    assert com_check is None


def test_supprimer_commentaire_inexistant():
    """Suppression d'un commentaire inexistant -> False"""
    ok = CommentaireDao().supprimer(99999, 999)
    assert ok is False


@pytest.mark.parametrize(
    "id_commentaire, id_utilisateur, expected",
    [
        (None, 1, False),
        (1, None, False),
        ("x", 1, False),
        (1, "y", False),
    ],
)
def test_supprimer_commentaire_entrees_invalides(
    id_commentaire, id_utilisateur, expected
):
    assert CommentaireDao().supprimer(id_commentaire, id_utilisateur) is expected


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
