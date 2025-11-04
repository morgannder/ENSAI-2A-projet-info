from unittest.mock import MagicMock
import pytest

from service.inventaire_service import InventaireService
from dao.inventaire_dao import InventaireDao
from business_object.ingredient import Ingredient


# -----------------------------
# Jeux de données de base
# -----------------------------

ING_LISTE = [
    Ingredient(id_ingredient=244, nom_ingredient="Light Rum", desc_ingredient="desc"),
    Ingredient(id_ingredient=251, nom_ingredient="Lime", desc_ingredient=None),
    Ingredient(id_ingredient=379, nom_ingredient="Sugar", desc_ingredient="desc"),
]


# -----------------------------
# Tests lister
# -----------------------------

def test_lister_ok():
    """La DAO renvoie une liste d'ingrédients -> le service la relaie telle quelle."""
    # GIVEN
    InventaireDao().consulter_inventaire = MagicMock(return_value=ING_LISTE)

    # WHEN
    lst = InventaireService().lister(3)

    # THEN
    assert lst == ING_LISTE
    InventaireDao().consulter_inventaire.assert_called_once_with(3)


def test_lister_id_invalide():
    """Id utilisateur invalide -> [] sans appeler la DAO."""
    # GIVEN
    InventaireDao().consulter_inventaire = MagicMock(return_value=ING_LISTE)

    # WHEN
    res = InventaireService().lister("x")

    # THEN
    assert res == []
    InventaireDao().consulter_inventaire.assert_not_called()


# -----------------------------
# Tests ajouter
# -----------------------------

def test_ajouter_ok():
    """Ajout via DAO -> True"""
    # GIVEN
    InventaireDao().ajouter_ingredient_inventaire = MagicMock(return_value=True)
    ing = Ingredient(id_ingredient=None, nom_ingredient="Mint", desc_ingredient=None)

    # WHEN
    res = InventaireService().ajouter(3, ing)

    # THEN
    assert res
    InventaireDao().ajouter_ingredient_inventaire.assert_called_once()


def test_ajouter_objet_invalide():
    """L'objet passé n'est pas un Ingredient -> False et DAO non appelée."""
    # GIVEN
    InventaireDao().ajouter_ingredient_inventaire = MagicMock(return_value=True)

    # WHEN
    res = InventaireService().ajouter(3, "pas-un-ingredient")

    # THEN
    assert res is False
    InventaireDao().ajouter_ingredient_inventaire.assert_not_called()


# -----------------------------
# Tests supprimer
# -----------------------------

def test_supprimer_ok():
    """Suppression d'un ingrédient de l'inventaire perso -> True"""
    # GIVEN
    InventaireDao().supprimer_ingredient = MagicMock(return_value=True)

    # WHEN
    res = InventaireService().supprimer(3, 244)

    # THEN
    assert res
    InventaireDao().supprimer_ingredient.assert_called_once_with(3, 244)


def test_supprimer_echec():
    """DAO renvoie False -> service renvoie False"""
    # GIVEN
    InventaireDao().supprimer_ingredient = MagicMock(return_value=False)

    # WHEN
    res = InventaireService().supprimer(3, 99999)

    # THEN
    assert not res

# -----------------------------
# Tests contient
# -----------------------------

def test_contient_par_id_oui():
    """Recherche par id présente."""
    # GIVEN
    InventaireDao().consulter_inventaire = MagicMock(return_value=ING_LISTE)

    # WHEN
    res = InventaireService().contient(3, 244)

    # THEN
    assert res


def test_contient_par_id_non():
    """Recherche par id absente."""
    # GIVEN
    InventaireDao().consulter_inventaire = MagicMock(return_value=ING_LISTE)

    # WHEN
    res = InventaireService().contient(3, 408)

    # THEN
    assert not res


def test_contient_par_nom_oui_insensible_casse():
    """Recherche par nom (case-insensitive, trim)."""
    # GIVEN
    InventaireDao().consulter_inventaire = MagicMock(return_value=ING_LISTE)

    # WHEN
    res = InventaireService().contient(3, "  light RUM  ")

    # THEN
    assert res


def test_contient_par_nom_non():
    """Nom absent."""
    # GIVEN
    InventaireDao().consulter_inventaire = MagicMock(return_value=ING_LISTE)

    # WHEN
    res = InventaireService().contient(3, "Coke")

    # THEN
    assert not res


def test_contient_id_invalide():
    """Id utilisateur invalide -> False direct."""
    # GIVEN
    # (rien)

    # WHEN
    res = InventaireService().contient("x", 244)

    # THEN
    assert res is False


# -----------------------------
# Tests supprimer_par_nom
# -----------------------------

def test_supprimer_par_nom_trouve():
    """On trouve l'ingrédient par nom, on appelle la suppression DAO avec le bon id."""
    # GIVEN
    InventaireDao().consulter_inventaire = MagicMock(return_value=ING_LISTE)
    InventaireDao().supprimer_ingredient = MagicMock(return_value=True)

    # WHEN
    res = InventaireService().supprimer_par_nom(3, "lime")

    # THEN
    assert res
    InventaireDao().supprimer_ingredient.assert_called_once_with(3, 251)


def test_supprimer_par_nom_introuvable():
    """Aucun ingrédient ne correspond au nom donné."""
    # GIVEN
    InventaireDao().consulter_inventaire = MagicMock(return_value=ING_LISTE)
    InventaireDao().supprimer_ingredient = MagicMock(return_value=True)

    # WHEN
    res = InventaireService().supprimer_par_nom(3, "Coke")

    # THEN
    assert not res
    InventaireDao().supprimer_ingredient.assert_not_called()


def test_supprimer_par_nom_nom_vide():
    """Nom vide/blanc -> False et DAO non appelée."""
    # GIVEN
    InventaireDao().consulter_inventaire = MagicMock(return_value=ING_LISTE)
    InventaireDao().supprimer_ingredient = MagicMock(return_value=True)

    # WHEN
    res = InventaireService().supprimer_par_nom(3, "   ")

    # THEN
    assert not res
    InventaireDao().supprimer_ingredient.assert_not_called()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
