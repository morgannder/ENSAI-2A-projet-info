import os
import pytest

from unittest.mock import patch

from utils.reset_database import ResetDatabase
from utils.securite import hash_password

from dao.inventaire_dao import InventaireDao

from business_object.inventaire import Inventaire


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test"""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


def test_trouver_par_id_existant():
    """Recherche par id d'un inventaire existant"""

    # GIVEN
    id_inventaire = 998

    # WHEN
    inventaire = InventaireDao().trouver_par_id(id_inventaire)

    # THEN
    assert inventaire is not None


def test_trouver_par_id_non_existant():
    """Recherche par id d'un inventaire n'existant pas"""

    # GIVEN
    id_inventaire = 9999999999999

    # WHEN
    inventaire = InventaireDao().trouver_par_id(id_inventaire)

    # THEN
    assert inventaire is None


def test_lister_tous():
    """Vérifie que la méthode renvoie une liste de Inventaire
    de taille supérieure ou égale à 2
    """

    # GIVEN

    # WHEN
    inventaires = InventaireDao().lister_tous()

    # THEN
    assert isinstance(inventaires, list)
    for j in inventaires:
        assert isinstance(j, Inventaire)
    assert len(inventaires) >= 2


def test_creer_ok():
    """Création de Inventaire réussie"""

    # GIVEN
    inventaire = Inventaire(pseudo="gg", age=44, mail="test@test.io")

    # WHEN
    creation_ok = InventaireDao().creer(inventaire)

    # THEN
    assert creation_ok
    assert inventaire.id_inventaire


def test_creer_ko():
    """Création de Inventaire échouée (age et mail incorrects)"""

    # GIVEN
    inventaire = Inventaire(pseudo="gg", age="chaine de caractere", mail=12)

    # WHEN
    creation_ok = InventaireDao().creer(inventaire)

    # THEN
    assert not creation_ok


def test_modifier_ok():
    """Modification de Inventaire réussie"""

    # GIVEN
    new_mail = "maurice@mail.com"
    inventaire = Inventaire(id_inventaire=997, pseudo="maurice", age=20, mail=new_mail)

    # WHEN
    modification_ok = InventaireDao().modifier(inventaire)

    # THEN
    assert modification_ok


def test_modifier_ko():
    """Modification de Inventaire échouée (id inconnu)"""

    # GIVEN
    inventaire = Inventaire(id_inventaire=8888, pseudo="id inconnu", age=1, mail="no@mail.com")

    # WHEN
    modification_ok = InventaireDao().modifier(inventaire)

    # THEN
    assert not modification_ok


def test_supprimer_ok():
    """Suppression de Inventaire réussie"""

    # GIVEN
    inventaire = Inventaire(id_inventaire=995, pseudo="miguel", age=1, mail="miguel@projet.fr")

    # WHEN
    suppression_ok = InventaireDao().supprimer(inventaire)

    # THEN
    assert suppression_ok


def test_supprimer_ko():
    """Suppression de Inventaire échouée (id inconnu)"""

    # GIVEN
    inventaire = Inventaire(id_inventaire=8888, pseudo="id inconnu", age=1, mail="no@z.fr")

    # WHEN
    suppression_ok = InventaireDao().supprimer(inventaire)

    # THEN
    assert not suppression_ok


def test_se_connecter_ok():
    """Connexion de Inventaire réussie"""

    # GIVEN
    pseudo = "batricia"
    mdp = "9876"

    # WHEN
    inventaire = InventaireDao().se_connecter(pseudo, hash_password(mdp, pseudo))

    # THEN
    assert isinstance(inventaire, Inventaire)


def test_se_connecter_ko():
    """Connexion de Inventaire échouée (pseudo ou mdp incorrect)"""

    # GIVEN
    pseudo = "toto"
    mdp = "poiuytreza"

    # WHEN
    inventaire = InventaireDao().se_connecter(pseudo, hash_password(mdp, pseudo))

    # THEN
    assert not inventaire


if __name__ == "__main__":
    pytest.main([__file__])
