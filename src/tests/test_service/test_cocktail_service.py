from unittest.mock import MagicMock

import pytest

from business_object.cocktail import Cocktail
from dao.cocktail_dao import CocktailDao
from service.cocktail_service import CocktailService

# ----- données de test -----

cocktail1 = Cocktail(
    id_cocktail=1,
    nom_cocktail="Mojito",
    alcoolise_cocktail="Alcoholic",
    categ_cocktail="Cocktail",
    image_cocktail="mojito.png",
    instruc_cocktail="Mélanger le rhum, le sucre et le citron",
)

cocktail2 = Cocktail(
    id_cocktail=4,
    nom_cocktail="Eau fraîche",
    alcoolise_cocktail="Non alcoholic",
    categ_cocktail="Soft Drink",
    image_cocktail="eau.png",
    instruc_cocktail="Servir de l'eau bien fraîche dans un verre",
)

cocktail3 = Cocktail(
    id_cocktail=3,
    nom_cocktail="Margarita",
    alcoolise_cocktail="Alcoholic",
    categ_cocktail="Cocktail",
    image_cocktail="margarita.png",
    instruc_cocktail="Mélanger la tequila, le triple sec et le citron",
)

liste_cocktails = [cocktail1, cocktail2, cocktail3]


def test_rechercher_par_filtre_ok():
    """Recherche par filtre renvoie les cocktails attendus"""
    # GIVEN
    CocktailDao().rechercher_cocktails = MagicMock(return_value=liste_cocktails)
    CocktailDao().lister_categories = MagicMock(return_value=["Cocktail"])
    CocktailDao().lister_verres = MagicMock(return_value=["Highball glass"])
    service = CocktailService()

    # WHEN
    res = service.rechercher_par_filtre(est_majeur=True, nom_cocktail="Mojito")

    # THEN
    assert len(res) == 3
    assert res[0].nom_cocktail == "Mojito"


def test_lister_cocktails_complets_ok():
    """Lister cocktails complets"""
    # GIVEN
    CocktailDao().cocktail_complet = MagicMock(return_value=liste_cocktails)
    service = CocktailService()

    # WHEN
    res = service.lister_cocktails_complets(id_utilisateur=1, est_majeur=True)

    # THEN
    assert len(res) == 3


def test_lister_cocktails_complets_mineur():
    """Lister cocktails complets pour mineur filtre alcool"""
    # GIVEN
    CocktailDao().cocktail_complet = MagicMock(return_value=liste_cocktails)
    service = CocktailService()

    # WHEN
    res = service.lister_cocktails_complets(id_utilisateur=1, est_majeur=False)

    # THEN
    assert all(c.alcoolise_cocktail == "Non alcoholic" for c in res)


def test_lister_cocktails_partiels_ok():
    """Lister cocktails partiels avec nb_manquants valide"""
    # GIVEN
    CocktailDao().cocktail_partiel = MagicMock(return_value=liste_cocktails)
    service = CocktailService()

    # WHEN
    res = service.lister_cocktails_partiels(
        nb_manquants=1, id_utilisateur=1, est_majeur=True
    )

    # THEN
    assert len(res) == 3


def test_lister_cocktails_partiels_nb_manquants_invalide():
    """Exception si nb_manquants invalide"""
    # GIVEN
    service = CocktailService()

    # WHEN / THEN
    with pytest.raises(ValueError):
        service.lister_cocktails_partiels(
            nb_manquants=6, id_utilisateur=1, est_majeur=True
        )


def test_cocktails_aleatoires_ok():
    """Cocktails aléatoires"""
    # GIVEN
    CocktailDao().cocktails_aleatoires = MagicMock(return_value=liste_cocktails)
    service = CocktailService()

    # WHEN
    res = service.cocktails_aleatoires(nb=3)

    # THEN
    assert len(res) == 3


def test_cocktails_aleatoires_nb_invalide():
    """Exception si nb invalide"""
    # GIVEN
    service = CocktailService()

    # WHEN / THEN
    with pytest.raises(ValueError):
        service.cocktails_aleatoires(nb=6)


def test_obtenir_cocktail_par_id_ok():
    """Obtenir cocktail par id"""
    # GIVEN
    CocktailDao().trouver_par_id = MagicMock(return_value=cocktail1)
    service = CocktailService()

    # WHEN
    res = service.obtenir_cocktail_par_id(1)

    # THEN
    assert res.id_cocktail == 1


def test_obtenir_cocktail_par_id_invalide():
    """Exception si id invalide"""
    # GIVEN
    service = CocktailService()

    # WHEN / THEN
    with pytest.raises(ValueError):
        service.obtenir_cocktail_par_id(-1)


def test_lister_tous_cocktails_ok():
    """Lister tous les cocktails"""
    # GIVEN
    CocktailDao().lister_tous = MagicMock(return_value=liste_cocktails)
    service = CocktailService()

    # WHEN
    res = service.lister_tous_cocktails()

    # THEN
    assert len(res) == 3


def test_lister_categories_verres():
    """Lister catégories et verres"""
    # GIVEN
    CocktailDao().lister_categories = MagicMock(return_value=["Cocktail", "Shot"])
    CocktailDao().lister_verres = MagicMock(
        return_value=["Highball glass", "Martini glass"]
    )
    service = CocktailService()

    # WHEN
    categories = service.lister_categories()
    verres = service.lister_verres()

    # THEN
    assert categories == ["Cocktail", "Shot"]
    assert verres == ["Highball glass", "Martini glass"]


if __name__ == "__main__":
    pytest.main([__file__])
