from unittest.mock import MagicMock

import pytest

from business_object.cocktail import Cocktail
from business_object.cocktail_complet import CocktailComplet
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
    res = service.lister_cocktails_partiels(nb_manquants=1, id_utilisateur=1, est_majeur=True)

    # THEN
    assert len(res) == 3


def test_lister_cocktails_partiels_nb_manquants_invalide():
    """Exception si nb_manquants invalide"""
    # GIVEN
    service = CocktailService()

    # WHEN / THEN
    with pytest.raises(ValueError):
        service.lister_cocktails_partiels(nb_manquants=6, id_utilisateur=1, est_majeur=True)


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


# Ajoutez ces tests à votre fichier test_cocktail_service.py


def test_rechercher_par_filtre_alcool_invalide():
    """Exception si type d'alcool invalide"""
    # GIVEN
    service = CocktailService()

    # WHEN / THEN
    with pytest.raises(ValueError) as exc_info:
        service.rechercher_par_filtre(alcool="Invalid")
    assert "Le type d'alcool doit être" in str(exc_info.value)


def test_rechercher_par_filtre_mineur_avec_alcool():
    """Exception si mineur demande des cocktails alcoolisés"""
    # GIVEN
    service = CocktailService()

    # WHEN / THEN
    with pytest.raises(ValueError) as exc_info:
        service.rechercher_par_filtre(est_majeur=False, alcool="Alcoholic")
    assert "Zéro alcool pour les mineurs" in str(exc_info.value)


def test_rechercher_par_filtre_mineur_filtrage_automatique():
    """Filtrage automatique pour mineur"""
    # GIVEN
    CocktailDao().rechercher_cocktails = MagicMock(return_value=liste_cocktails)
    service = CocktailService()

    # WHEN
    res = service.rechercher_par_filtre(est_majeur=False)

    # THEN
    assert len(res) == 1
    assert res[0].alcoolise_cocktail == "Non alcoholic"


def test_lister_cocktails_complets_sans_utilisateur():
    """Exception si pas d'ID utilisateur"""
    # GIVEN
    service = CocktailService()

    # WHEN / THEN
    with pytest.raises(ValueError) as exc_info:
        service.lister_cocktails_complets(id_utilisateur=None, est_majeur=True)
    assert "connexion est requise" in str(exc_info.value)


def test_lister_cocktails_partiels_sans_utilisateur():
    """Exception si pas d'ID utilisateur pour cocktails partiels"""
    # GIVEN
    service = CocktailService()

    # WHEN / THEN
    with pytest.raises(ValueError) as exc_info:
        service.lister_cocktails_partiels(nb_manquants=1, id_utilisateur=None, est_majeur=True)
    assert "connexion est requise" in str(exc_info.value)


def test_lister_cocktails_partiels_nb_manquants_negatif():
    """Exception si nb_manquants négatif"""
    # GIVEN
    service = CocktailService()

    # WHEN / THEN
    with pytest.raises(ValueError) as exc_info:
        service.lister_cocktails_partiels(nb_manquants=-1, id_utilisateur=1, est_majeur=True)
    assert "doit être compris entre 0 et 5" in str(exc_info.value)


def test_cocktails_aleatoires_mineur_filtrage():
    """Filtrage automatique pour mineur sur cocktails aléatoires"""
    # GIVEN
    CocktailDao().cocktails_aleatoires = MagicMock(return_value=liste_cocktails)
    service = CocktailService()

    # WHEN
    res = service.cocktails_aleatoires(est_majeur=False, nb=2)

    # THEN
    assert len(res) == 1
    assert res[0].alcoolise_cocktail == "Non alcoholic"


def test_cocktails_aleatoires_limite_superieure():
    """Vérifie que le service bloque si on demande plus que 5"""
    # GIVEN
    service = CocktailService()

    # WHEN / THEN - Le service doit lever une exception si on demande plus que 5
    with pytest.raises(ValueError) as exc_info:
        service.cocktails_aleatoires(nb=10)

    assert "Le nombre de cocktails doit être entre 1 et 5" in str(exc_info.value)


def test_obtenir_cocktail_par_id_non_trouve():
    """Retourne None si cocktail non trouvé"""
    # GIVEN
    CocktailDao().trouver_par_id = MagicMock(return_value=None)
    service = CocktailService()

    # WHEN
    res = service.obtenir_cocktail_par_id(999)

    # THEN
    assert res is None


def test_realiser_cocktail_par_id_ok():
    """Test de realiser_cocktail par ID"""
    # GIVEN
    cocktail_complet = MagicMock(spec=CocktailComplet)
    CocktailDao().realiser_cocktail = MagicMock(return_value=cocktail_complet)
    service = CocktailService()

    # WHEN
    res = service.realiser_cocktail(id_cocktail=1, langue="FR")

    # THEN
    assert res == cocktail_complet
    CocktailDao().realiser_cocktail.assert_called_once_with(
        id_cocktail=1, nom_cocktail=None, langue="FR"
    )


def test_realiser_cocktail_par_nom_ok():
    """Test de realiser_cocktail par nom"""
    # GIVEN
    cocktail_complet = MagicMock(spec=CocktailComplet)
    CocktailDao().realiser_cocktail = MagicMock(return_value=cocktail_complet)
    service = CocktailService()

    # WHEN
    res = service.realiser_cocktail(nom_cocktail="Mojito", langue="ENG")

    # THEN
    assert res == cocktail_complet
    CocktailDao().realiser_cocktail.assert_called_once_with(
        id_cocktail=None, nom_cocktail="Mojito", langue="ENG"
    )


def test_realiser_cocktail_non_trouve():
    """Exception si realiser_cocktail ne trouve rien"""
    # GIVEN
    CocktailDao().realiser_cocktail = MagicMock(return_value=None)
    service = CocktailService()

    # WHEN / THEN
    with pytest.raises(ValueError) as exc_info:
        service.realiser_cocktail(id_cocktail=999)
    assert "Zéro cocktail trouvé" in str(exc_info.value)


def test_obtenir_ingredients_par_cocktails_ok():
    """Test obtenir_ingredients_par_cocktails"""
    # GIVEN
    ingredients_attendus = {1: ["Rhum", "Menthe"], 2: ["Vodka", "Jus d'orange"]}
    CocktailDao().obtenir_ingredients_par_cocktails = MagicMock(return_value=ingredients_attendus)
    service = CocktailService()

    # WHEN
    res = service.obtenir_ingredients_par_cocktails([1, 2])

    # THEN
    assert res == ingredients_attendus
    CocktailDao().obtenir_ingredients_par_cocktails.assert_called_once_with([1, 2])


def test_obtenir_ingredients_par_cocktails_liste_vide():
    """Test obtenir_ingredients_par_cocktails avec liste vide"""
    # GIVEN
    service = CocktailService()

    # WHEN
    res = service.obtenir_ingredients_par_cocktails([])

    # THEN
    assert res == {}


def test_obtenir_ingredients_possedes_par_cocktails_ok():
    """Test obtenir_ingredients_possedes_par_cocktails"""
    # GIVEN
    ingredients_attendus = {1: ["Rhum", "Menthe"], 2: ["Vodka"]}
    CocktailDao().obtenir_ingredients_possedes_par_cocktails = MagicMock(
        return_value=ingredients_attendus
    )
    service = CocktailService()

    # WHEN
    res = service.obtenir_ingredients_possedes_par_cocktails(id_utilisateur=1, id_cocktails=[1, 2])

    # THEN
    assert res == ingredients_attendus
    CocktailDao().obtenir_ingredients_possedes_par_cocktails.assert_called_once_with(
        id_utilisateur=1, id_cocktails=[1, 2]
    )


def test_obtenir_ingredients_possedes_par_cocktails_liste_vide():
    """Test obtenir_ingredients_possedes_par_cocktails avec liste vide"""
    # GIVEN
    service = CocktailService()

    # WHEN
    res = service.obtenir_ingredients_possedes_par_cocktails(id_utilisateur=1, id_cocktails=[])

    # THEN
    assert res == {}


def test_rechercher_par_filtre_retourne_liste_vide():
    """Gestion des résultats vides pour rechercher_par_filtre"""
    # GIVEN
    CocktailDao().rechercher_cocktails = MagicMock(return_value=[])
    service = CocktailService()

    # WHEN
    res = service.rechercher_par_filtre(est_majeur=True)

    # THEN
    assert res == []


def test_lister_cocktails_complets_retourne_liste_vide():
    """Gestion des résultats vides pour lister_cocktails_complets"""
    # GIVEN
    CocktailDao().cocktail_complet = MagicMock(return_value=[])
    service = CocktailService()

    # WHEN
    res = service.lister_cocktails_complets(id_utilisateur=1, est_majeur=True)

    # THEN
    assert res == []


if __name__ == "__main__":
    pytest.main([__file__])
