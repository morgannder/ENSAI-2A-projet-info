from unittest.mock import MagicMock

from service.cocktail_service import CocktailService

from dao.cocktail_dao import CocktailDao

from business_object.cocktail import Cocktail


liste_cocktails = [
    Cocktail(pseudo="jp", age="10", mail="jp@mail.fr", mdp="1234"),
    Cocktail(pseudo="lea", age="10", mail="lea@mail.fr", mdp="0000"),
    Cocktail(pseudo="gg", age="10", mail="gg@mail.fr", mdp="abcd"),
]


def test_creer_ok():
    """ "Création de Cocktail réussie"""

    # GIVEN
    pseudo, mdp, age, mail, fan_pokemon = "jp", "1234", 15, "z@mail.oo", True
    CocktailDao().creer = MagicMock(return_value=True)

    # WHEN
    cocktail = CocktailService().creer(pseudo, mdp, age, mail, fan_pokemon)

    # THEN
    assert cocktail.pseudo == pseudo


def test_creer_echec():
    """Création de Cocktail échouée
    (car la méthode CocktailDao().creer retourne False)"""

    # GIVEN
    pseudo, mdp, age, mail, fan_pokemon = "jp", "1234", 15, "z@mail.oo", True
    CocktailDao().creer = MagicMock(return_value=False)

    # WHEN
    cocktail = CocktailService().creer(pseudo, mdp, age, mail, fan_pokemon)

    # THEN
    assert cocktail is None


def test_lister_tous_inclure_mdp_true():
    """Lister les Cocktails en incluant les mots de passe"""

    # GIVEN
    CocktailDao().lister_tous = MagicMock(return_value=liste_cocktails)

    # WHEN
    res = CocktailService().lister_tous(inclure_mdp=True)

    # THEN
    assert len(res) == 3
    for cocktail in res:
        assert cocktail.mdp is not None


def test_lister_tous_inclure_mdp_false():
    """Lister les Cocktails en excluant les mots de passe"""

    # GIVEN
    CocktailDao().lister_tous = MagicMock(return_value=liste_cocktails)

    # WHEN
    res = CocktailService().lister_tous()

    # THEN
    assert len(res) == 3
    for cocktail in res:
        assert not cocktail.mdp


def test_pseudo_deja_utilise_oui():
    """Le pseudo est déjà utilisé dans liste_cocktails"""

    # GIVEN
    pseudo = "lea"

    # WHEN
    CocktailDao().lister_tous = MagicMock(return_value=liste_cocktails)
    res = CocktailService().pseudo_deja_utilise(pseudo)

    # THEN
    assert res


def test_pseudo_deja_utilise_non():
    """Le pseudo n'est pas utilisé dans liste_cocktails"""

    # GIVEN
    pseudo = "chaton"

    # WHEN
    CocktailDao().lister_tous = MagicMock(return_value=liste_cocktails)
    res = CocktailService().pseudo_deja_utilise(pseudo)

    # THEN
    assert not res


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
