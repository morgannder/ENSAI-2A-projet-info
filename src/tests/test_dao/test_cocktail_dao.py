import os
from unittest.mock import Mock, patch

import pytest

from business_object.cocktail import Cocktail
from business_object.cocktail_complet import CocktailComplet
from dao.cocktail_dao import CocktailDao
from dao.db_connection import DBConnection
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
    est_majeur = True

    # WHEN
    cocktails = CocktailDao().cocktail_complet(id_utilisateur, est_majeur)

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
    est_majeur = True
    # WHEN
    cocktails = CocktailDao().cocktail_complet(id_utilisateur, est_majeur)

    # THEN
    assert isinstance(cocktails, list)
    assert len(cocktails) == 0  # Aucun cocktail réalisable complètement


def test_cocktail_complet_pagination():
    """Test que la pagination est appliquée"""
    # GIVEN
    dao = CocktailDao()

    with patch.object(DBConnection, "connection") as mock_conn:
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = []

        # WHEN
        result = dao.cocktail_complet(
            est_majeur=True, id_utilisateur=3, limite=5, decalage=10
        )

        # THEN
        assert result == []

        mock_cursor = (
            mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        )
        assert mock_cursor.execute.called


# -------------------- TEST 2 : Cocktails partiels --------------------


def test_cocktail_partiel(setup_test_environment):
    """Utilisateur peut faire Mojito et Old Fashioned"""

    # Given
    id_utilisateur = 3
    nb_manquants = 2
    est_majeur = True

    # WHEN
    cocktails = CocktailDao().cocktail_partiel(id_utilisateur, nb_manquants, est_majeur)

    # THEN
    assert isinstance(cocktails, list)
    for c in cocktails:
        assert isinstance(c, Cocktail)
        print(c.nom_cocktail)

    noms = [c.nom_cocktail for c in cocktails]
    assert len(cocktails) == 2
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
    est_majeur = True

    # WHEN
    cocktails = CocktailDao().rechercher_cocktails(
        est_majeur, nom_cocktail, categorie, verre, alcool
    )

    # THEN
    assert len(cocktails) == 1
    c = cocktails[0]
    assert c.nom_cocktail == "Coke and Drops"


# -------------------- TEST 4 : Cocktails aléatoires --------------------


def test_cocktails_aleatoires(setup_test_environment):
    """La méthode doit retourner entre 1 et 5 cocktails"""

    # GIVEN
    nb = 2
    est_majeur = True

    # WHEN
    cocktails = CocktailDao().cocktails_aleatoires(est_majeur, nb)

    # THEN
    assert 1 <= len(cocktails) <= 2
    for c in cocktails:
        assert isinstance(c, Cocktail)
        assert c.nom_cocktail


def test_cocktails_aleatoires_limite(setup_test_environment):
    """Même si on demande plus de 10, le max doit être 5."""

    cocktails = CocktailDao().cocktails_aleatoires(50)
    assert len(cocktails) <= 5


# ==================== Tests pour realiser_cocktail ====================


def test_realiser_cocktail_par_id_succes(setup_test_environment):
    """Test récupération cocktail par ID avec succès"""
    # GIVEN
    dao = CocktailDao()
    mock_row = {
        "id_cocktail": 1,
        "nom_cocktail": "Mojito",
        "categorie": "Classic",
        "alcool": True,
        "image_url": "mojito.jpg",
        "verre": "Highball",
        "instructions": "Mix all ingredients",
        "ingredients": "Rum|||Mint|||Lime",
        "quantites": "50ml|||10 leaves|||1/2",
    }

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )
        mock_cursor.fetchone.return_value = mock_row

        result = dao.realiser_cocktail(id_cocktail=1)

    # THEN
    assert isinstance(result, CocktailComplet)
    assert result.id_cocktail == 1
    assert result.nom_cocktail == "Mojito"


def test_realiser_cocktail_par_nom_succes(setup_test_environment):
    """Test récupération cocktail par nom avec succès"""
    # GIVEN
    dao = CocktailDao()
    mock_row = {
        "id_cocktail": 2,
        "nom_cocktail": "Margarita",
        "categorie": "Classic",
        "alcool": True,
        "image_url": "margarita.jpg",
        "verre": "Margarita",
        "instructions": "Shake with ice",
        "ingredients": "Tequila|||Lime|||Triple Sec",
        "quantites": "50ml|||25ml|||20ml",
    }

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )
        mock_cursor.fetchone.return_value = mock_row

        result = dao.realiser_cocktail(nom_cocktail="Margarita")

    # THEN
    assert result.nom_cocktail == "Margarita"


def test_realiser_cocktail_sans_params_raises_error(setup_test_environment):
    """Test erreur quand aucun paramètre n'est fourni"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN
    with pytest.raises(
        ValueError, match="Vous devez fournir soit un ID, soit un nom de cocktail"
    ):
        dao.realiser_cocktail()


def test_realiser_cocktail_introuvable(setup_test_environment):
    """Test retour None quand cocktail n'existe pas"""
    # GIVEN
    dao = CocktailDao()

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )
        mock_cursor.fetchone.return_value = None

        result = dao.realiser_cocktail(id_cocktail=999)

    # THEN
    assert result is None


# ==================== Tests pour trouver_par_id ====================


def test_trouver_par_id_succes(setup_test_environment):
    """Test recherche cocktail par ID"""
    # GIVEN
    dao = CocktailDao()
    mock_row = {
        "id_cocktail": 1,
        "nom_cocktail": "Mojito",
        "categorie": "Classic",
        "alcool": True,
        "image_url": "mojito.jpg",
        "instructions": "Mix ingredients",
    }

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )
        mock_cursor.fetchone.return_value = mock_row

        result = dao.trouver_par_id(1)

    # THEN
    assert isinstance(result, Cocktail)
    assert result.id_cocktail == 1


def test_trouver_par_id_introuvable(setup_test_environment):
    """Test retour None quand ID n'existe pas"""
    # GIVEN
    dao = CocktailDao()

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )
        mock_cursor.fetchone.return_value = None

        result = dao.trouver_par_id(999)

    # THEN
    assert result is None


# ==================== Tests pour obtenir_ingredients_par_cocktails ====================


def test_obtenir_ingredients_par_cocktails_succes(setup_test_environment):
    """Test récupération ingrédients pour plusieurs cocktails"""
    # GIVEN
    dao = CocktailDao()
    mock_rows = [
        {"id_cocktail": 1, "ingredients": "Rum|||Mint|||Lime"},
        {"id_cocktail": 2, "ingredients": "Tequila|||Lime|||Salt"},
    ]

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )
        mock_cursor.fetchall.return_value = mock_rows

        result = dao.obtenir_ingredients_par_cocktails([1, 2])

    # THEN
    assert result == {1: ["Rum", "Mint", "Lime"], 2: ["Tequila", "Lime", "Salt"]}


def test_obtenir_ingredients_par_cocktails_liste_vide(setup_test_environment):
    """Test retour dict vide quand liste d'IDs vide"""
    # GIVEN
    dao = CocktailDao()

    # WHEN
    result = dao.obtenir_ingredients_par_cocktails([])

    # THEN
    assert result == {}


# ==================== Tests pour obtenir_ingredients_possedes_par_cocktails ====================


def test_obtenir_ingredients_possedes_succes(setup_test_environment):
    """Test récupération ingrédients possédés"""
    # GIVEN
    dao = CocktailDao()
    mock_rows = [{"id_cocktail": 1, "ingredients_possedes": "Rum|||Lime"}]

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )
        mock_cursor.fetchall.return_value = mock_rows

        result = dao.obtenir_ingredients_possedes_par_cocktails(1, [1, 2])

    # THEN
    assert result == {1: ["Rum", "Lime"]}


def test_obtenir_ingredients_possedes_liste_vide(setup_test_environment):
    """Test retour dict vide quand liste d'IDs vide"""
    # GIVEN
    dao = CocktailDao()

    # WHEN
    result = dao.obtenir_ingredients_possedes_par_cocktails(1, [])

    # THEN
    assert result == {}


# ==================== Tests d'erreurs de base de données ====================


def test_cocktail_complet_erreur_bdd(setup_test_environment):
    """Test gestion d'erreur DB dans cocktail_complet"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_conn.__enter__.side_effect = Exception("Simulated DB failure")

        with pytest.raises(Exception):
            dao.cocktail_complet(id_utilisateur=1)


def test_cocktail_partiel_erreur_bdd(setup_test_environment):
    """Test gestion d'erreur DB dans cocktail_partiel"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_conn.__enter__.side_effect = Exception("Simulated DB failure")

        with pytest.raises(Exception):
            dao.cocktail_partiel(id_utilisateur=1, nb_manquants=2)


def test_rechercher_cocktails_erreur_bdd(setup_test_environment):
    """Test gestion d'erreur DB dans rechercher_cocktails"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_conn.__enter__.side_effect = Exception("Simulated DB failure")

        with pytest.raises(Exception):
            dao.rechercher_cocktails()


def test_cocktails_aleatoires_erreur_bdd(setup_test_environment):
    """Test gestion d'erreur DB dans cocktails_aleatoires"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_conn.__enter__.side_effect = Exception("Simulated DB failure")

        with pytest.raises(Exception):
            dao.cocktails_aleatoires(3)


def test_realiser_cocktail_erreur_bdd(setup_test_environment):
    """Test gestion d'erreur de base de données"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_conn.__enter__.side_effect = Exception("DB error")

        with pytest.raises(Exception):
            dao.realiser_cocktail(id_cocktail=1)


def test_obtenir_ingredients_par_cocktails_erreur_bdd(setup_test_environment):
    """Test retour dict vide en cas d'erreur DB"""
    # GIVEN
    dao = CocktailDao()

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_conn.__enter__.side_effect = Exception("DB error")

        result = dao.obtenir_ingredients_par_cocktails([1, 2])

    # THEN
    assert result == {}


def test_trouver_par_id_erreur_bdd(setup_test_environment):
    """Test gestion d'erreur DB dans trouver_par_id"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_conn.__enter__.side_effect = Exception("Simulated DB failure")

        with pytest.raises(Exception):
            dao.trouver_par_id(1)


def test_obtenir_ingredients_possedes_par_cocktails_erreur_bdd(setup_test_environment):
    """Test gestion d'erreur DB dans obtenir_ingredients_possedes_par_cocktails"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_conn.__enter__.side_effect = Exception("Simulated DB failure")

        result = dao.obtenir_ingredients_possedes_par_cocktails(1, [1, 2])
        assert result == {}


if __name__ == "__main__":
    pytest.main([__file__])
