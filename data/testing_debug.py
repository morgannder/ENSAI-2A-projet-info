import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv


class IngredientSearch:
    def __init__(self):
        self.conn = None
        self.load_env()
        self.connect()

    def load_env(self):
        """Charge les variables d'environnement depuis .env"""
        try:
            # Charge le fichier .env à la racine du projet
            load_dotenv()
            self.db_config = {
                "host": os.getenv("POSTGRES_HOST"),
                "database": os.getenv("POSTGRES_DATABASE"),
                "user": os.getenv("POSTGRES_USER"),
                "password": os.getenv("POSTGRES_PASSWORD"),
                "port": os.getenv("POSTGRES_PORT", "5432"),
            }
            print("✅ Variables d'environnement chargées")
        except Exception as e:
            print(f"❌ Erreur lors du chargement du .env: {e}")
            self.db_config = {}

    def connect(self):
        """Connexion à la base de données"""
        try:
            # Vérification des paramètres requis
            required_params = ["database", "user", "password"]
            missing_params = [
                param for param in required_params if not self.db_config.get(param)
            ]

            if missing_params:
                print(f"❌ Paramètres manquants dans .env: {', '.join(missing_params)}")
                return

            self.conn = psycopg2.connect(
                host=self.db_config["host"],
                database=self.db_config["database"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                port=self.db_config["port"],
            )
            print("✅ Connexion à la base de données réussie")

        except Exception as e:
            print(f"❌ Erreur de connexion à la base de données: {e}")
            print("Vérifie ton fichier .env et la connexion à la base")

    def search_by_name(self, nom):
        """Recherche par nom d'ingrédient"""
        if not self.conn:
            print("❌ Pas de connexion à la base de données")
            return []

        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM ingredient WHERE nom_ingredient ILIKE %s ORDER BY nom_ingredient",
                (f"%{nom}%",),
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return []

    def search_by_id(self, id_ingredient):
        """Recherche par ID"""
        if not self.conn:
            print("❌ Pas de connexion à la base de données")
            return []

        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM ingredient WHERE id_ingredient = %s", (id_ingredient,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return []

    def get_all_ingredients(self, limit=20):
        """Tous les ingrédients"""
        if not self.conn:
            print("❌ Pas de connexion à la base de données")
            return []

        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                f"SELECT * FROM ingredient ORDER BY nom_ingredient LIMIT {limit}"
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return []

    def search_by_alcohol(self, has_alcohol=True):
        """Recherche les ingrédients alcoolisés ou non"""
        if not self.conn:
            print("❌ Pas de connexion à la base de données")
            return []

        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            # Cette requête suppose que tu as un champ pour l'alcool dans ta table
            # Si ce n'est pas le cas, on peut l'adapter
            cursor.execute(
                "SELECT * FROM ingredient WHERE nom_ingredient ILIKE ANY(%s) ORDER BY nom_ingredient",
                (
                    [
                        (
                            "%alcool%",
                            "%liquor%",
                            "%spirit%",
                            "%whisky%",
                            "%vodka%",
                            "%gin%",
                        )
                    ]
                    if has_alcohol
                    else [("%juice%", "%soda%", "%water%", "%syrup%")]
                ),
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return []

    def display_results(self, results):
        """Affichage des résultats"""
        if not results:
            print("❌ Aucun résultat trouvé")
            return

        print(f"\n🎯 {len(results)} résultat(s) trouvé(s) :")
        for i, row in enumerate(results, 1):
            print(
                f"\n{i}. ID: {row['id_ingredient']} | 📛 Nom: {row['nom_ingredient']}"
            )
            if row["desc_ingredient"] and row["desc_ingredient"].strip():
                desc = (
                    row["desc_ingredient"][:150] + "..."
                    if len(row["desc_ingredient"]) > 150
                    else row["desc_ingredient"]
                )
                print(f"   📝 Description: {desc}")
            print("   " + "-" * 50)

    def test_connection(self):
        """Test la connexion et affiche quelques stats"""
        if not self.conn:
            print("❌ Pas de connexion à la base de données")
            return False

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM ingredient")
            total = cursor.fetchone()[0]
            print(f"📊 Total d'ingrédients dans la base: {total}")

            cursor.execute(
                "SELECT nom_ingredient FROM ingredient ORDER BY RANDOM() LIMIT 3"
            )
            samples = cursor.fetchall()
            print("🎲 Exemples d'ingrédients:", ", ".join([s[0] for s in samples]))

            return True
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            return False

    def interactive_menu(self):
        """Menu interactif"""
        if not self.conn:
            print("❌ Impossible de démarrer le menu - connexion DB échouée")
            return

        # Test de la connexion au démarrage
        if not self.test_connection():
            return

        while True:
            print("\n" + "=" * 60)
            print("🔍 RECHERCHE D'INGRÉDIENTS - BASE DE DONNÉES COCKTAILS")
            print("=" * 60)
            print("1. 🔎 Rechercher par nom")
            print("2. 🔢 Rechercher par ID")
            print("3. 📋 Voir tous les ingrédients")
            print("4. 📊 Statistiques de la base")
            print("5. 🚪 Quitter")

            choix = input("\n🎯 Votre choix (1-5): ").strip()

            if choix == "1":
                nom = input("📛 Nom de l'ingrédient (ou partie du nom): ").strip()
                if nom:
                    results = self.search_by_name(nom)
                    self.display_results(results)
                else:
                    print("❌ Veuillez entrer un nom à rechercher")

            elif choix == "2":
                try:
                    id_ing = int(input("🔢 ID de l'ingrédient: ").strip())
                    results = self.search_by_id(id_ing)
                    self.display_results(results)
                except ValueError:
                    print("❌ L'ID doit être un nombre")

            elif choix == "3":
                try:
                    limit = int(
                        input("📋 Nombre d'ingrédients à afficher (défaut: 20): ")
                        or "20"
                    )
                    results = self.get_all_ingredients(limit)
                    self.display_results(results)
                except ValueError:
                    print("❌ Le nombre doit être un entier")

            elif choix == "4":
                self.test_connection()

            elif choix == "5":
                print("👋 Au revoir ! À bientôt pour de nouveaux cocktails 🍸")
                break

            else:
                print("❌ Choix invalide. Veuillez choisir entre 1 et 5.")

    def __del__(self):
        if self.conn:
            self.conn.close()
            print("🔌 Connexion à la base de données fermée")


# Point d'entrée principal
if __name__ == "__main__":
    # Démarrer l'application
    print("🚀 Démarrage de l'outil de recherche d'ingrédients...")
    search_tool = IngredientSearch()
    search_tool.interactive_menu()
