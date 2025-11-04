from unittest.mock import MagicMock
import pytest

from dao.inventaire_dao import InventaireDao
from dao import db_connection as db_module
from business_object.ingredient import Ingredient


def _patch_db(monkeypatch, cursor_mock: MagicMock):
    # GIVEN
    cursor_cm = MagicMock()
    cursor_cm.__enter__.return_value = cursor_mock
    cursor_cm.__exit__.return_value = False

    connection_mock = MagicMock()
    connection_mock.cursor.return_value = cursor_cm

    connection_cm = MagicMock()
    connection_cm.__enter__.return_value = connection_mock
    connection_cm.__exit__.return_value = False

    fake_db = MagicMock()
    fake_db.connection = connection_cm

    # WHEN
    monkeypatch.setattr(db_module, "DBConnection", lambda: fake_db)


def test_ajouter_ingredient_inventaire_cree_nouveau(monkeypatch):
    """Ingrédient sans id, introuvable -> INSERT RETURNING id, puis lien inventaire."""
    # GIVEN
    cursor = MagicMock()
    cursor.fetchone.side_effect = [None, {"id_ingredient": 999}]
    _patch_db(monkeypatch, cursor)
    ing = Ingredient(
        id_ingredient=None, nom_ingredient="NouveauGin", desc_ingredient="desc"
    )

    # WHEN
    ok = InventaireDao().ajouter_ingredient_inventaire(3, ing)

    # THEN
    assert ok is True
    assert ing.id_ingredient == 999
    assert (
        cursor.execute.call_count >= 2
    )  # SELECT + INSERT ingredient + INSERT inventaire (>=2)


def test_ajouter_ingredient_inventaire_existant_par_nom(monkeypatch):
    """Ingrédient sans id mais déjà présent (SELECT renvoie un id) -> lien inventaire."""
    # GIVEN
    cursor = MagicMock()
    cursor.fetchone.side_effect = [{"id_ingredient": 244}]
    _patch_db(monkeypatch, cursor)
    ing = Ingredient(
        id_ingredient=None, nom_ingredient="Light Rum", desc_ingredient=None
    )

    # WHEN
    ok = InventaireDao().ajouter_ingredient_inventaire(3, ing)

    # THEN
    assert ok is True
    assert ing.id_ingredient in (None, 244)
    assert cursor.execute.call_count >= 2


def test_ajouter_ingredient_inventaire_avec_id_deja_renseigne(monkeypatch):
    """Ingrédient avec id -> pas de SELECT/INSERT sur ingredient, seulement lien inventaire."""
    # GIVEN
    cursor = MagicMock()
    _patch_db(monkeypatch, cursor)
    ing = Ingredient(
        id_ingredient=18, nom_ingredient="Angostura Bitters", desc_ingredient="desc"
    )

    # WHEN
    ok = InventaireDao().ajouter_ingredient_inventaire(5, ing)

    # THEN
    assert ok is True
    assert cursor.execute.call_count >= 1


@pytest.mark.parametrize(
    "user_id, ing, expected",
    [
        (
            0,
            Ingredient(id_ingredient=None, nom_ingredient="x", desc_ingredient=None),
            False,
        ),
        (
            -1,
            Ingredient(id_ingredient=None, nom_ingredient="x", desc_ingredient=None),
            False,
        ),
        (1, None, False),
        (
            1,
            Ingredient(id_ingredient=None, nom_ingredient="   ", desc_ingredient=None),
            False,
        ),
    ],
)
def test_ajouter_ingredient_inventaire_entrees_invalides(
    monkeypatch, user_id, ing, expected
):
    # GIVEN
    cursor = MagicMock()
    _patch_db(monkeypatch, cursor)

    # WHEN
    res = InventaireDao().ajouter_ingredient_inventaire(user_id, ing)

    # THEN
    assert res is expected
    cursor.execute.assert_not_called()


def test_ajouter_ingredient_inventaire_exception(monkeypatch):
    """Exception d'exécution SQL -> False."""
    # GIVEN
    cursor = MagicMock()
    cursor.execute.side_effect = RuntimeError("boom execute")
    _patch_db(monkeypatch, cursor)
    ing = Ingredient(id_ingredient=None, nom_ingredient="Boom", desc_ingredient=None)

    # WHEN
    res = InventaireDao().ajouter_ingredient_inventaire(2, ing)

    # THEN
    assert res is False


# ------------------------------
# Tests supprimer_ingredient
# ------------------------------


def test_supprimer_ingredient_succes(monkeypatch):
    """Suppression du lien utilisateur/ingrédient -> True si rowcount > 0."""
    # GIVEN
    cursor = MagicMock()
    cursor.rowcount = 1
    _patch_db(monkeypatch, cursor)

    # WHEN
    res = InventaireDao().supprimer_ingredient(3, 244)

    # THEN
    assert res is True
    cursor.execute.assert_called_once()
    called_sql, called_params = cursor.execute.call_args[0]
    assert "id_utilisateur" in called_sql and "id_ingredient" in called_sql
    assert called_params["idu"] == 3 and called_params["idi"] == 244


def test_supprimer_ingredient_aucune_ligne(monkeypatch):
    """Suppression sans ligne affectée -> False."""
    # GIVEN
    cursor = MagicMock()
    cursor.rowcount = 0
    _patch_db(monkeypatch, cursor)

    # WHEN
    res = InventaireDao().supprimer_ingredient(3, 99999)

    # THEN
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
def test_supprimer_ingredient_entrees_invalides(monkeypatch, user_id, ing_id, expected):
    # GIVEN
    cursor = MagicMock()
    _patch_db(monkeypatch, cursor)

    # WHEN
    res = InventaireDao().supprimer_ingredient(user_id, ing_id)

    # THEN
    assert res is expected
    cursor.execute.assert_not_called()


def test_supprimer_ingredient_exception(monkeypatch):
    """Exception pendant le DELETE -> False."""
    # GIVEN
    cursor = MagicMock()
    cursor.execute.side_effect = RuntimeError("boom")
    _patch_db(monkeypatch, cursor)

    # WHEN
    res = InventaireDao().supprimer_ingredient(3, 244)

    # THEN
    assert res is False


# ------------------------------
# Tests consulter_inventaire
# ------------------------------


def test_consulter_inventaire_retour_dicts(monkeypatch):
    """fetchall renvoie des dicts -> mapping via clés."""
    # GIVEN
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        {
            "id_ingredient": 244,
            "nom_ingredient": "Light Rum",
            "desc_ingredient": "desc",
        },
        {"id_ingredient": 251, "nom_ingredient": "Lime", "desc_ingredient": None},
    ]
    _patch_db(monkeypatch, cursor)

    # WHEN
    lst = InventaireDao().consulter_inventaire(3)

    # THEN
    assert len(lst) == 2
    assert lst[0].id_ingredient == 244
    assert lst[1].nom_ingredient == "Lime"


def test_consulter_inventaire_retour_tuples(monkeypatch):
    """fetchall renvoie des tuples -> mapping via indices."""
    # GIVEN
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        (379, "Sugar", "desc"),
        (361, "Soda Water", None),
    ]
    _patch_db(monkeypatch, cursor)

    # WHEN
    lst = InventaireDao().consulter_inventaire(3)

    # THEN
    assert [x.id_ingredient for x in lst] == [379, 361]
    assert lst[1].desc_ingredient is None


def test_consulter_inventaire_aucun_resultat(monkeypatch):
    """Aucun ingrédient -> liste vide."""
    # GIVEN
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    _patch_db(monkeypatch, cursor)

    # WHEN
    res = InventaireDao().consulter_inventaire(3)

    # THEN
    assert res == []


def test_consulter_inventaire_id_invalide():
    """Id utilisateur invalide -> court-circuit, pas d'appel DB, liste vide."""
    # GIVEN
    # (rien)

    # WHEN
    res = InventaireDao().consulter_inventaire("x")

    # THEN
    assert res == []


def test_consulter_inventaire_exception(monkeypatch):
    """Exception pendant la requête -> []"""
    # GIVEN
    cursor = MagicMock()
    cursor.execute.side_effect = RuntimeError("boom")
    _patch_db(monkeypatch, cursor)

    # WHEN
    res = InventaireDao().consulter_inventaire(3)

    # THEN
    assert res == []


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
