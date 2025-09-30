import os
import pytest

from unittest.mock import patch

from utils.reset_database import ResetDatabase
from utils.securite import hash_password

from dao.cocktail_dao import CocktailDao

from business_object.cocktail import Cocktail


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test"""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


def test_trouver_par_id_existant():
    """Recherche par id d'un cocktail existant"""

    # GIVEN
    id_cocktail = 998

    # WHEN
    cocktail = CocktailDao().trouver_par_id(id_cocktail)

    # THEN
    assert cocktail is not None


def test_trouver_par_id_non_existant():
    """Recherche par id d'un cocktail n'existant pas"""

    # GIVEN
    id_cocktail = 9999999999999

    # WHEN
    cocktail = CocktailDao().trouver_par_id(id_cocktail)

    # THEN
    assert cocktail is None


def test_lister_tous():
    """Vérifie que la méthode renvoie une liste de Cocktail
    de taille supérieure ou égale à 2
    """

    # GIVEN

    # WHEN
    cocktails = CocktailDao().lister_tous()

    # THEN
    assert isinstance(cocktails, list)
    for j in cocktails:
        assert isinstance(j, Cocktail)
    assert len(cocktails) >= 2


def test_creer_ok():
    """Création de Cocktail réussie"""

    # GIVEN
    cocktail = Cocktail(pseudo="gg", age=44, mail="test@test.io")

    # WHEN
    creation_ok = CocktailDao().creer(cocktail)

    # THEN
    assert creation_ok
    assert cocktail.id_cocktail


def test_creer_ko():
    """Création de Cocktail échouée (age et mail incorrects)"""

    # GIVEN
    cocktail = Cocktail(pseudo="gg", age="chaine de caractere", mail=12)

    # WHEN
    creation_ok = CocktailDao().creer(cocktail)

    # THEN
    assert not creation_ok


def test_modifier_ok():
    """Modification de Cocktail réussie"""

    # GIVEN
    new_mail = "maurice@mail.com"
    cocktail = Cocktail(id_cocktail=997, pseudo="maurice", age=20, mail=new_mail)

    # WHEN
    modification_ok = CocktailDao().modifier(cocktail)

    # THEN
    assert modification_ok


def test_modifier_ko():
    """Modification de Cocktail échouée (id inconnu)"""

    # GIVEN
    cocktail = Cocktail(id_cocktail=8888, pseudo="id inconnu", age=1, mail="no@mail.com")

    # WHEN
    modification_ok = CocktailDao().modifier(cocktail)

    # THEN
    assert not modification_ok


def test_supprimer_ok():
    """Suppression de Cocktail réussie"""

    # GIVEN
    cocktail = Cocktail(id_cocktail=995, pseudo="miguel", age=1, mail="miguel@projet.fr")

    # WHEN
    suppression_ok = CocktailDao().supprimer(cocktail)

    # THEN
    assert suppression_ok


def test_supprimer_ko():
    """Suppression de Cocktail échouée (id inconnu)"""

    # GIVEN
    cocktail = Cocktail(id_cocktail=8888, pseudo="id inconnu", age=1, mail="no@z.fr")

    # WHEN
    suppression_ok = CocktailDao().supprimer(cocktail)

    # THEN
    assert not suppression_ok


def test_se_connecter_ok():
    """Connexion de Cocktail réussie"""

    # GIVEN
    pseudo = "batricia"
    mdp = "9876"

    # WHEN
    cocktail = CocktailDao().se_connecter(pseudo, hash_password(mdp, pseudo))

    # THEN
    assert isinstance(cocktail, Cocktail)


def test_se_connecter_ko():
    """Connexion de Cocktail échouée (pseudo ou mdp incorrect)"""

    # GIVEN
    pseudo = "toto"
    mdp = "poiuytreza"

    # WHEN
    cocktail = CocktailDao().se_connecter(pseudo, hash_password(mdp, pseudo))

    # THEN
    assert not cocktail


if __name__ == "__main__":
    pytest.main([__file__])
