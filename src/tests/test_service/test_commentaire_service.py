from unittest.mock import MagicMock

import pytest

from business_object.commentaire import Commentaire
from dao.commentaire_dao import CommentaireDao
from service.commentaire_service import CommentaireService

# -----------------------------
# Jeux de données test
# -----------------------------
COM_LISTE = [
    Commentaire(
        id_commentaire=1,
        id_utilisateur=3,
        id_cocktail=0,
        texte="Super rafraîchissant !",
        note=5,
        pseudo_utilisateur="Alice",
        date_creation="2025-04-11 17:00:00",
    ),
    Commentaire(
        id_commentaire=2,
        id_utilisateur=5,
        id_cocktail=0,
        texte="Trop sucré à mon goût.",
        note=3,
        pseudo_utilisateur="Bob",
        date_creation="2025-04-11 17:15:00",
    ),
]


# -----------------------------
# Tests lister
# -----------------------------
def test_lister_commentaires_ok():
    """La DAO renvoie une liste -> le service la relaie."""
    CommentaireDao().trouver_par_cocktail = MagicMock(return_value=COM_LISTE)
    service = CommentaireService()

    lst = service.lister_commentaires_cocktail(0)

    assert lst == COM_LISTE
    CommentaireDao().trouver_par_cocktail.assert_called_once_with(0)


def test_lister_commentaires_aucun():
    """Si aucun commentaire, retourne liste vide."""
    CommentaireDao().trouver_par_cocktail = MagicMock(return_value=[])
    service = CommentaireService()

    lst = service.lister_commentaires_cocktail(999)

    assert lst == []
    CommentaireDao().trouver_par_cocktail.assert_called_once_with(999)


# -----------------------------
# Tests obtenir commentaire utilisateur
# -----------------------------
def test_obtenir_commentaire_utilisateur_ok():
    """Renvoie un commentaire existant."""
    CommentaireDao().trouver_par_utilisateur_et_cocktail = MagicMock(return_value=COM_LISTE[0])
    service = CommentaireService()

    com = service.obtenir_commentaire_utilisateur(3, 0)

    assert com == COM_LISTE[0]
    CommentaireDao().trouver_par_utilisateur_et_cocktail.assert_called_once_with(3, 0)


def test_obtenir_commentaire_utilisateur_aucun():
    """Renvoie None si pas de commentaire."""
    CommentaireDao().trouver_par_utilisateur_et_cocktail = MagicMock(return_value=None)
    service = CommentaireService()

    com = service.obtenir_commentaire_utilisateur(999, 0)

    assert com is None
    CommentaireDao().trouver_par_utilisateur_et_cocktail.assert_called_once_with(999, 0)


# -----------------------------
# Tests calculer note moyenne
# -----------------------------
def test_calculer_note_moyenne_ok():
    """Calcule correctement la note moyenne."""
    CommentaireDao().trouver_par_cocktail = MagicMock(return_value=COM_LISTE)
    service = CommentaireService()

    moyenne = service.calculer_note_moyenne(0)

    expected = sum(c.note for c in COM_LISTE) / len(COM_LISTE)
    assert moyenne == expected


def test_calculer_note_moyenne_aucun_commentaire():
    """Retourne 0 si pas de commentaire."""
    CommentaireDao().trouver_par_cocktail = MagicMock(return_value=[])
    service = CommentaireService()

    assert service.calculer_note_moyenne(999) == 0


# -----------------------------
# Tests ajouter commentaire
# -----------------------------
def test_ajouter_commentaire_ok():
    """Ajout réussi via DAO"""
    CommentaireDao().trouver_par_utilisateur_et_cocktail = MagicMock(return_value=None)
    CommentaireDao().creer = MagicMock(return_value=True)
    service = CommentaireService()

    res = service.ajouter_commentaire(1, 0, "Top cocktail", 5)

    assert res
    CommentaireDao().creer.assert_called_once()


def test_ajouter_commentaire_deja_existant():
    """Erreur si l'utilisateur a déjà commenté"""
    CommentaireDao().trouver_par_utilisateur_et_cocktail = MagicMock(return_value=COM_LISTE[0])
    service = CommentaireService()

    with pytest.raises(ValueError):
        service.ajouter_commentaire(3, 0, "Encore un commentaire", 4)


def test_ajouter_commentaire_texte_vide():
    """Erreur si texte vide"""
    service = CommentaireService()
    with pytest.raises(ValueError):
        service.ajouter_commentaire(1, 0, "   ", 4)


def test_ajouter_commentaire_note_invalide():
    """Erreur si note hors 1-5"""
    service = CommentaireService()
    with pytest.raises(ValueError):
        service.ajouter_commentaire(1, 0, "Texte", 6)


# -----------------------------
# Tests supprimer commentaire
# -----------------------------
def test_supprimer_commentaire_ok():
    """Suppression réussie"""
    CommentaireDao().supprimer = MagicMock(return_value=True)
    service = CommentaireService()

    res = service.supprimer_commentaire(3, 1)

    assert res
    CommentaireDao().supprimer.assert_called_once_with(1, 3)


def test_supprimer_commentaire_echec():
    """Suppression échouée"""
    CommentaireDao().supprimer = MagicMock(return_value=False)
    service = CommentaireService()

    res = service.supprimer_commentaire(3, 1)

    assert res is False
    CommentaireDao().supprimer.assert_called_once_with(1, 3)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
