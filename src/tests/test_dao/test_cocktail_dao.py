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


# ==================== Tests pour realiser_cocktail ====================


def test_realiser_cocktail_par_id_success(setup_test_environment):
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
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = mock_row

        result = dao.realiser_cocktail(id_cocktail=1)

    # THEN
    assert isinstance(result, CocktailComplet)
    assert result.id_cocktail == 1
    assert result.nom_cocktail == "Mojito"


def test_realiser_cocktail_par_nom_success(setup_test_environment):
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
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = mock_row

        result = dao.realiser_cocktail(nom_cocktail="Margarita")

    # THEN
    assert result.nom_cocktail == "Margarita"


def test_realiser_cocktail_no_params_raises_error(setup_test_environment):
    """Test erreur quand aucun paramètre n'est fourni"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN
    with pytest.raises(ValueError, match="Vous devez fournir soit un ID, soit un nom de cocktail"):
        dao.realiser_cocktail()


def test_realiser_cocktail_not_found(setup_test_environment):
    """Test retour None quand cocktail n'existe pas"""
    # GIVEN
    dao = CocktailDao()

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = dao.realiser_cocktail(id_cocktail=999)

    # THEN
    assert result is None


def test_realiser_cocktail_database_error(setup_test_environment):
    """Test gestion d'erreur de base de données"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_conn.__enter__.side_effect = Exception("DB error")

        with pytest.raises(Exception):
            dao.realiser_cocktail(id_cocktail=1)


# ==================== Tests pour cocktail_complet ====================


def test_cocktail_complet_success(setup_test_environment):
    """Test récupération cocktails complets avec inventaire"""
    # GIVEN
    dao = CocktailDao()
    mock_rows = [
        {
            "id_cocktail": 1,
            "nom_cocktail": "Mojito",
            "categorie": "Classic",
            "alcool": True,
            "image_url": "mojito.jpg",
            "verre": "Highball",
            "instructions": "Mix ingredients",
        }
    ]

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = mock_rows

        result = dao.cocktail_complet(id_utilisateur=1, langue="FRA", limite=5, decalage=0)

    # THEN
    assert len(result) == 1
    assert isinstance(result[0], Cocktail)
    assert result[0].nom_cocktail == "Mojito"


def test_cocktail_complet_empty_result(setup_test_environment):
    """Test retour liste vide quand aucun cocktail trouvé"""
    # GIVEN
    dao = CocktailDao()

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        result = dao.cocktail_complet(id_utilisateur=1)

    # THEN
    assert result == []


def test_cocktail_complet_pagination():
    """Test que la pagination est appliquée"""
    # GIVEN
    dao = CocktailDao()

    with patch.object(DBConnection, "connection") as mock_conn:
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = []

        # WHEN
        result = dao.cocktail_complet(id_utilisateur=3, limite=5, decalage=10)

        # THEN
        assert result == []  # Car fetchall retourne une liste vide

        mock_cursor = mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        assert mock_cursor.execute.called


# ==================== Tests pour cocktail_partiel ====================


def test_cocktail_partiel_success(setup_test_environment):
    """Test récupération cocktails partiels avec ingrédients manquants"""
    # GIVEN
    dao = CocktailDao()
    mock_rows = [
        {
            "id_cocktail": 1,
            "nom_cocktail": "Mojito",
            "categorie": "Classic",
            "alcool": True,
            "image_url": "mojito.jpg",
            "verre": "Highball",
            "instructions": "Mix ingredients",
        }
    ]

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = mock_rows

        result = dao.cocktail_partiel(id_utilisateur=1, nb_manquants=2, langue="ENG")

    # THEN
    assert len(result) == 1
    assert result[0].nom_cocktail == "Mojito"


# ==================== Tests pour rechercher_cocktails ====================


def test_rechercher_cocktails_sans_filtres(setup_test_environment):
    """Test recherche sans filtres"""
    # GIVEN
    dao = CocktailDao()
    mock_rows = [
        {
            "id_cocktail": 1,
            "nom_cocktail": "Mojito",
            "categorie": "Classic",
            "alcool": True,
            "image_url": "mojito.jpg",
            "verre": "Highball",
            "instructions": "Mix ingredients",
        }
    ]

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = mock_rows

        result = dao.rechercher_cocktails()

    # THEN
    assert len(result) == 1


# ==================== Tests pour cocktails_aleatoires ====================


def test_cocktails_aleatoires_success(setup_test_environment):
    """Test récupération cocktails aléatoires"""
    # GIVEN
    dao = CocktailDao()
    mock_rows = [
        {
            "id_cocktail": 1,
            "nom_cocktail": "Mojito",
            "categorie": "Classic",
            "alcool": True,
            "image_url": "mojito.jpg",
            "verre": "Highball",
            "instructions": "Mix ingredients",
        }
    ]

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = mock_rows

        result = dao.cocktails_aleatoires(nombre=3, langue="FRA")

    # THEN
    assert len(result) == 1


# ==================== Tests pour instruction_column ====================


def test_instruction_column_langues_supportees(setup_test_environment):
    """Test mapping des colonnes d'instructions par langue"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN
    assert dao.instruction_column("ENG") == "instructions"
    assert dao.instruction_column("FRA") == "instructions_fr"
    assert dao.instruction_column("ESP") == "instructions_es"
    assert dao.instruction_column("GER") == "instructions_de"
    assert dao.instruction_column("ITA") == "instructions_it"


def test_instruction_column_langue_inconnue(setup_test_environment):
    """Test langue non supportée retourne colonne par défaut"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN
    assert dao.instruction_column("CHINOIS") == "instructions"
    assert dao.instruction_column("") == "instructions"


# ==================== Tests pour trouver_par_id ====================


def test_trouver_par_id_success(setup_test_environment):
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
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = mock_row

        result = dao.trouver_par_id(1)

    # THEN
    assert isinstance(result, Cocktail)
    assert result.id_cocktail == 1


def test_trouver_par_id_not_found(setup_test_environment):
    """Test retour None quand ID n'existe pas"""
    # GIVEN
    dao = CocktailDao()

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = dao.trouver_par_id(999)

    # THEN
    assert result is None


# ==================== Tests pour obtenir_ingredients_par_cocktails ====================


def test_obtenir_ingredients_par_cocktails_success(setup_test_environment):
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
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = mock_rows

        result = dao.obtenir_ingredients_par_cocktails([1, 2])

    # THEN
    assert result == {1: ["Rum", "Mint", "Lime"], 2: ["Tequila", "Lime", "Salt"]}


def test_obtenir_ingredients_par_cocktails_empty_list(setup_test_environment):
    """Test retour dict vide quand liste d'IDs vide"""
    # GIVEN
    dao = CocktailDao()

    # WHEN
    result = dao.obtenir_ingredients_par_cocktails([])

    # THEN
    assert result == {}


def test_obtenir_ingredients_par_cocktails_database_error(setup_test_environment):
    """Test retour dict vide en cas d'erreur DB"""
    # GIVEN
    dao = CocktailDao()

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_conn.__enter__.side_effect = Exception("DB error")

        result = dao.obtenir_ingredients_par_cocktails([1, 2])

    # THEN
    assert result == {}


# ==================== Tests pour obtenir_ingredients_possedes_par_cocktails ====================


def test_obtenir_ingredients_possedes_success(setup_test_environment):
    """Test récupération ingrédients possédés"""
    # GIVEN
    dao = CocktailDao()
    mock_rows = [{"id_cocktail": 1, "ingredients_possedes": "Rum|||Lime"}]

    # WHEN
    with patch.object(DBConnection, "connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = mock_rows

        result = dao.obtenir_ingredients_possedes_par_cocktails(1, [1, 2])

    # THEN
    assert result == {1: ["Rum", "Lime"]}


def test_obtenir_ingredients_possedes_empty_list(setup_test_environment):
    """Test retour dict vide quand liste d'IDs vide"""
    # GIVEN
    dao = CocktailDao()

    # WHEN
    result = dao.obtenir_ingredients_possedes_par_cocktails(1, [])

    # THEN
    assert result == {}


# ==================== Tests d'intégration (optionnels) ====================


def test_singleton_pattern(setup_test_environment):
    """Test que CocktailDao suit le pattern Singleton"""
    # WHEN
    dao1 = CocktailDao()
    dao2 = CocktailDao()

    # THEN
    assert dao1 is dao2


def test_methods_use_correct_instruction_column(setup_test_environment):
    """Test que toutes les méthodes utilisent la bonne colonne d'instructions"""
    # GIVEN
    dao = CocktailDao()

    # WHEN & THEN - Vérifier que chaque méthode qui prend une langue utilise instruction_column
    with patch.object(dao, "instruction_column") as mock_method:
        mock_method.return_value = "instructions_fr"

        with patch.object(DBConnection, "connection") as mock_conn:
            mock_cursor = Mock()
            mock_conn.__enter__.return_value.cursor.return_value.__enter__.return_value = (
                mock_cursor
            )
            mock_cursor.fetchall.return_value = []

            # Appeler différentes méthodes avec langue FRA
            dao.cocktail_complet(1, "FRA")
            dao.cocktail_partiel(1, 2, "FRA")
            dao.rechercher_cocktails(langue="FRA")
            dao.cocktails_aleatoires(langue="FRA")

            # Vérifier que instruction_column a été appelé pour chaque méthode
            assert mock_method.call_count == 4


if __name__ == "__main__":
    pytest.main([__file__])
