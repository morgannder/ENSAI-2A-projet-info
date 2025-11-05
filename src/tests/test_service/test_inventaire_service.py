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
# Tests de suggestions d'ingrédients
# -----------------------------
def test_suggerer_ingredients_ok():
    """La méthode renvoie bien une liste d'ingrédients"""
    # GIVEN
    InventaireDao().ingredients_aleatoires = MagicMock(return_value=ING_LISTE)
    service = InventaireService()

    # WHEN
    res = service.suggerer_ingredients(n=3)

    # THEN
    assert len(res) == 3
    for ing in res:
        assert isinstance(ing, Ingredient)
        assert ing.nom_ingredient


def test_suggerer_ingredients_nb_trop_grand():
    """Si on demande plus de 10, on borne à 10"""
    # GIVEN
    InventaireDao().ingredients_aleatoires = MagicMock(return_value=ING_LISTE)
    service = InventaireService()

    # WHEN
    res = service.suggerer_ingredients(n=50)

    # THEN
    assert isinstance(res, list)


def test_suggerer_ingredients_nb_trop_petit():
    """Si on demande moins de 1, on borne à 1"""
    # GIVEN
    InventaireDao().ingredients_aleatoires = MagicMock(return_value=ING_LISTE)
    service = InventaireService()

    # WHEN
    res = service.suggerer_ingredients(n=0)

    # THEN
    assert isinstance(res, list)


def test_suggerer_ingredients_type_invalide():
    """Erreur si n n'est pas un entier"""
    # GIVEN
    service = InventaireService()

    # WHEN / THEN
    try:
        service.suggerer_ingredients("trois")
        assert False
    except ValueError:
        assert True



if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
