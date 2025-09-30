from unittest.mock import MagicMock

from service.inventaire_service import InventaireService

from dao.inventaire_dao import InventaireDao

from business_object.inventaire import Inventaire


liste_inventaires = [
    Inventaire(pseudo="jp", age="10", mail="jp@mail.fr", mdp="1234"),
    Inventaire(pseudo="lea", age="10", mail="lea@mail.fr", mdp="0000"),
    Inventaire(pseudo="gg", age="10", mail="gg@mail.fr", mdp="abcd"),
]


def test_creer_ok():
    """ "Création de Inventaire réussie"""

    # GIVEN
    pseudo, mdp, age, mail, fan_pokemon = "jp", "1234", 15, "z@mail.oo", True
    InventaireDao().creer = MagicMock(return_value=True)

    # WHEN
    inventaire = InventaireService().creer(pseudo, mdp, age, mail, fan_pokemon)

    # THEN
    assert inventaire.pseudo == pseudo


def test_creer_echec():
    """Création de Inventaire échouée
    (car la méthode InventaireDao().creer retourne False)"""

    # GIVEN
    pseudo, mdp, age, mail, fan_pokemon = "jp", "1234", 15, "z@mail.oo", True
    InventaireDao().creer = MagicMock(return_value=False)

    # WHEN
    inventaire = InventaireService().creer(pseudo, mdp, age, mail, fan_pokemon)

    # THEN
    assert inventaire is None


def test_lister_tous_inclure_mdp_true():
    """Lister les Inventaires en incluant les mots de passe"""

    # GIVEN
    InventaireDao().lister_tous = MagicMock(return_value=liste_inventaires)

    # WHEN
    res = InventaireService().lister_tous(inclure_mdp=True)

    # THEN
    assert len(res) == 3
    for inventaire in res:
        assert inventaire.mdp is not None


def test_lister_tous_inclure_mdp_false():
    """Lister les Inventaires en excluant les mots de passe"""

    # GIVEN
    InventaireDao().lister_tous = MagicMock(return_value=liste_inventaires)

    # WHEN
    res = InventaireService().lister_tous()

    # THEN
    assert len(res) == 3
    for inventaire in res:
        assert not inventaire.mdp


def test_pseudo_deja_utilise_oui():
    """Le pseudo est déjà utilisé dans liste_inventaires"""

    # GIVEN
    pseudo = "lea"

    # WHEN
    InventaireDao().lister_tous = MagicMock(return_value=liste_inventaires)
    res = InventaireService().pseudo_deja_utilise(pseudo)

    # THEN
    assert res


def test_pseudo_deja_utilise_non():
    """Le pseudo n'est pas utilisé dans liste_inventaires"""

    # GIVEN
    pseudo = "chaton"

    # WHEN
    InventaireDao().lister_tous = MagicMock(return_value=liste_inventaires)
    res = InventaireService().pseudo_deja_utilise(pseudo)

    # THEN
    assert not res


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
