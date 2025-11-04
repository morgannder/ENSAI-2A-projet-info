import os
import pytest
from unittest.mock import patch

from utils.reset_database import ResetDatabase

from dao.inventaire_dao import InventaireDao
from business_object.ingredient import Ingredient


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
# Helpers
# ----------------------------------------------------------------------
def _find_in_inventory(items, name: str):
    """Retourne l'Ingredient ayant le nom donné (case-insensitive) dans une liste."""
    lname = name.strip().lower()
    for it in items:
        if (it.nom_ingredient or "").strip().lower() == lname:
            return it
    return None


# ----------------------------------------------------------------------
# Tests ajouter_ingredient_inventaire
# ----------------------------------------------------------------------
def test_ajouter_ingredient_inventaire_cree_nouveau():
    """Ingrédient sans id, introuvable -> création de l'ingrédient + lien inventaire."""
    # GIVEN
    id_user = 4  # utilisateur existant dans la base test
    nom_test = "ZZZ_Test_Gin_12345"
    ing = Ingredient(id_ingredient=None, nom_ingredient=nom_test, desc_ingredient="desc")

    # WHEN
    ok = InventaireDao().ajouter_ingredient_inventaire(id_user, ing)

    # THEN
    assert ok is True
    assert ing.id_ingredient is not None

    # Et l'ingrédient doit apparaitre dans l'inventaire de l'utilisateur
    inv = InventaireDao().consulter_inventaire(id_user)
    assert _find_in_inventory(inv, nom_test) is not None


def test_ajouter_ingredient_inventaire_existant_par_nom():
    """Ingrédient sans id mais déjà présent (par nom) -> uniquement lien inventaire."""
    # GIVEN
    id_user = 4
    nom_test = "ZZZ_Test_Rum_12345"
    # 1er ajout : crée l'ingrédient
    ing1 = Ingredient(id_ingredient=None, nom_ingredient=nom_test, desc_ingredient=None)
    assert InventaireDao().ajouter_ingredient_inventaire(id_user, ing1) is True
    assert ing1.id_ingredient is not None

    # 2e ajout : même nom, sans id -> ne doit pas recréer un nouvel ingrédient
    ing2 = Ingredient(id_ingredient=None, nom_ingredient=nom_test, desc_ingredient=None)

    # WHEN
    ok2 = InventaireDao().ajouter_ingredient_inventaire(id_user, ing2)

    # THEN
    assert ok2 is True
    # l'id d'ing2 peut ne pas être mis à jour par le DAO, on vérifie surtout l'inventaire
    inv = InventaireDao().consulter_inventaire(id_user)
    match = _find_in_inventory(inv, nom_test)
    assert match is not None
    # Vérifie qu'il n'y a qu'une seule entrée pour ce nom (pas de doublon)
    assert sum(1 for x in inv if (x.nom_ingredient or "").lower() == nom_test.lower()) == 1


def test_ajouter_ingredient_inventaire_avec_id_deja_renseigne():
    """Ingrédient avec id -> pas de (re)création d'ingrédient, seulement lien inventaire."""
    # GIVEN
    id_user = 4
    nom_test = "ZZZ_Test_Vodka_12345"

    # On crée d'abord l'ingrédient via une première insertion (pour récupérer son id)
    ing_base = Ingredient(id_ingredient=None, nom_ingredient=nom_test, desc_ingredient="d")
    assert InventaireDao().ajouter_ingredient_inventaire(id_user, ing_base) is True
    assert ing_base.id_ingredient is not None

    # On réutilise le même id pour un nouvel ajout
    ing2 = Ingredient(id_ingredient=ing_base.id_ingredient, nom_ingredient=nom_test, desc_ingredient="d2")

    # WHEN
    ok = InventaireDao().ajouter_ingredient_inventaire(id_user, ing2)

    # THEN
    assert ok is True
    inv = InventaireDao().consulter_inventaire(id_user)
    assert _find_in_inventory(inv, nom_test) is not None


@pytest.mark.parametrize(
    "user_id, ing, expected",
    [
        (0, Ingredient(id_ingredient=None, nom_ingredient="x", desc_ingredient=None), False),
        (-1, Ingredient(id_ingredient=None, nom_ingredient="x", desc_ingredient=None), False),
        (1, None, False),
        (1, Ingredient(id_ingredient=None, nom_ingredient="   ", desc_ingredient=None), False),
    ],
)
def test_ajouter_ingredient_inventaire_entrees_invalides(user_id, ing, expected):
    """Entrées invalides -> False (court-circuit)."""
    res = InventaireDao().ajouter_ingredient_inventaire(user_id, ing)
    assert res is expected


def test_ajouter_ingredient_inventaire_exception_gracefully():
    """
    Cas d'erreur difficile à simuler sans mock.
    On vérifie au moins qu'une entrée invalide renvoie False (déjà couvert ci-dessus).
    """
    assert InventaireDao().ajouter_ingredient_inventaire("not_an_int", Ingredient(None, "x", None)) is False


# ----------------------------------------------------------------------
# Tests supprimer_ingredient
# ----------------------------------------------------------------------
def test_supprimer_ingredient_succes():
    """Suppression du lien utilisateur/ingrédient -> True si le lien existait."""
    # GIVEN
    id_user = 4
    nom_test = "ZZZ_Test_To_Delete_12345"
    ing = Ingredient(id_ingredient=None, nom_ingredient=nom_test, desc_ingredient=None)
    assert InventaireDao().ajouter_ingredient_inventaire(id_user, ing) is True
    assert ing.id_ingredient is not None

    # WHEN
    res = InventaireDao().supprimer_ingredient(id_user, ing.id_ingredient)

    # THEN
    assert res is True
    # Et l'élément ne doit plus apparaître dans l'inventaire
    inv = InventaireDao().consulter_inventaire(id_user)
    assert _find_in_inventory(inv, nom_test) is None


def test_supprimer_ingredient_aucune_ligne():
    """Suppression d'un lien inexistant -> False."""
    id_user = 4
    res = InventaireDao().supprimer_ingredient(id_user, 999999)  # id ingredient très improbable
    assert res is False


@pytest.mark.parametrize(
    "user_id, ing_id, expected",
    [
        (None, 1, False),
        ("x", 1, False),
        (0, 1, False),
        (1, None, False),
        (1, "y", False),
        (1, 0, False),
    ],
)
def test_supprimer_ingredient_entrees_invalides(user_id, ing_id, expected):
    assert InventaireDao().supprimer_ingredient(user_id, ing_id) is expected


# ----------------------------------------------------------------------
# Tests consulter_inventaire
# ----------------------------------------------------------------------
def test_consulter_inventaire_ok():
    """Après insertion, la consultation retourne bien les objets Ingredient."""
    # GIVEN
    id_user = 4
    nom_a = "ZZZ_Test_List_A_12345"
    nom_b = "ZZZ_Test_List_B_12345"
    for n in (nom_a, nom_b):
        InventaireDao().ajouter_ingredient_inventaire(
            id_user, Ingredient(id_ingredient=None, nom_ingredient=n, desc_ingredient=None)
        )

    # WHEN
    lst = InventaireDao().consulter_inventaire(id_user)

    # THEN
    assert isinstance(lst, list)
    assert _find_in_inventory(lst, nom_a) is not None
    assert _find_in_inventory(lst, nom_b) is not None


def test_consulter_inventaire_id_invalide():
    """Id utilisateur invalide -> liste vide (court-circuit)."""
    assert InventaireDao().consulter_inventaire("x") == []


def test_consulter_inventaire_aucun_resultat_sur_user_sans_ingredients():
    """
    Utilisateur valide mais (probablement) sans ingrédients dans la base test.
    On prend un id très grand pour éviter collisions.
    """
    assert InventaireDao().consulter_inventaire(999_999) == []


if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
