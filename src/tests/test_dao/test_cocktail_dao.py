import os
from unittest.mock import patch

import pytest

from business_object.cocktail import Cocktail
from dao.cocktail_dao import CocktailDao
from utils.reset_database import ResetDatabase


@pytest.fixture(scope="session")
def setup_test_environment():
    """Initialisation des données de test"""
    with patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


# -------------------- TEST 1 : Cocktails réalisables complètement --------------------


def test_cocktail_complet_ok(setup_test_environment):
    """Utilisateur 3 possède tous les ingrédients pour Mojito et Old Fashioned."""

    # Given
    id_utilisateur = 3

    # WHEN
    cocktails = CocktailDao().cocktail_complet(id_utilisateur)

    # THEN
    assert isinstance(cocktails, list)
    for c in cocktails:
        assert isinstance(c, Cocktail)
        print(c.nom_cocktail)

    noms = sorted([c.nom_cocktail for c in cocktails])
    # D’après la base de test : John (id 3) a tous les ingrédients de Mojito mais pas un Old Fashioned ni de Long Island
    assert "Mojito" in noms  # 0 manquants
    assert "Long Island" not in noms  # 0 manquants
    assert "Old Fashioned" not in noms  # 0 manquants


def test_cocktail_complet_ko(setup_test_environment):
    """Utilisateur 6  n'a pas tous les ingrédients pour aucun cocktail."""

    # Given
    id_utilisateur = 6

    # WHEN
    cocktails = CocktailDao().cocktail_complet(id_utilisateur)

    # THEN
    assert isinstance(cocktails, list)
    assert len(cocktails) == 0  # Aucun cocktail réalisable complètement


# -------------------- TEST 2 : Cocktails partiels --------------------


def test_cocktail_partiel(setup_test_environment):
    """Utilisateur peut faire Mojito et Old Fashioned"""

    # Given
    id_utilisateur = 3
    nb_manquants = 2

    # WHEN
    cocktails = CocktailDao().cocktail_partiel(id_utilisateur, nb_manquants)

    # THEN
    assert isinstance(cocktails, list)
    for c in cocktails:
        assert isinstance(c, Cocktail)
        print(c.nom_cocktail)

    noms = [c.nom_cocktail for c in cocktails]
    assert len(cocktails) == 1
    assert "Mojito" not in noms  # 0 manquants
    assert "Old Fashioned" in noms  # 1 manquants
    assert "Long Island Tea" not in noms  # 4 manquants (trop)


# -------------------- TEST 3 : Recherche --------------------


def test_rechercher_multi_filtres(setup_test_environment):
    """Recherche combinant nom, catégorie, alcool  et verre."""

    # GIVEN
    alcool = "Non alcoholic"
    nom_cocktail = "Coke"
    categorie = "Soft Drink"
    verre = "Cocktail glass"

    # WHEN
    cocktails = CocktailDao().rechercher_cocktails(nom_cocktail, categorie, verre, alcool)

    # THEN
    assert len(cocktails) == 1  # on s'attend à un seul cocktail correspondant
    c = cocktails[0]
    assert c.nom_cocktail == "Coke and Drops"


# -------------------- TEST 4 : Cocktails aléatoires --------------------


def test_cocktails_aleatoires(setup_test_environment):
    """La méthode doit retourner entre 1 et 5 cocktails"""

    # GIVEN
    nb = 2

    # WHEN
    cocktails = CocktailDao().cocktails_aleatoires(nb)

    # THEN
    assert 1 <= len(cocktails) <= 2
    for c in cocktails:
        assert isinstance(c, Cocktail)
        assert c.nom_cocktail  # le nom doit être présent


def test_cocktails_aleatoires_limite(setup_test_environment):
    """Même si on demande plus de 10, le max doit être 5."""

    cocktails = CocktailDao().cocktails_aleatoires(50)
    assert len(cocktails) <= 5


if __name__ == "__main__":
    pytest.main([__file__])
