import json
import time
from pathlib import Path

import requests


def extract_cocktails_by_id():
    """
    Extrait tous les cocktails par leur ID en parcourant une plage d'IDs
    et sauvegarde les résultats dans extractAPI/extract_by_id/
    """
    # Configuration des paths
    output_dir = Path("extractAPI/extract_by_id")
    output_dir.mkdir(parents=True, exist_ok=True)

    base_url = "https://www.thecocktaildb.com/api/json/v1/1/lookup.php?iid="

    # Plage d'ID à tester (basée sur les connaissances de l'API TheCocktailDB)
    start_id = 0  # ID minimum connu
    end_id = 1500  # ID maximum estimé

    found_cocktails = []
    total_requests = 0
    successful_requests = 0

    print("🍸 Extraction des cocktails par ID")
    print("=" * 50)
    print(f"📁 Répertoire de sortie : {output_dir.absolute()}")
    print(f"🔍 Plage d'IDs recherchée : {start_id} à {end_id}")
    print(f"📊 Nombre total d'IDs à tester : {end_id - start_id + 1}")
    print("Cette opération peut prendre plusieurs minutes...")
    print("-" * 50)

    for cocktail_id in range(start_id, end_id + 1):
        url = f"{base_url}{cocktail_id}"

        try:
            # Faire la requête API
            response = requests.get(url, timeout=10)
            total_requests += 1

            if response.status_code == 200:
                data = response.json()

                # Vérifier si un cocktail existe pour cet ID
                if data.get("ingredients") is not None:
                    cocktail = data["ingredients"][0]
                    found_cocktails.append(cocktail)
                    successful_requests += 1

                    # Sauvegarde individuelle du cocktail
                    cocktail_file = output_dir / f"ingredient_{cocktail_id}.json"
                    with open(cocktail_file, "w", encoding="utf-8") as f:
                        json.dump(cocktail, f, indent=2, ensure_ascii=False)

                    print(f"✅ ID {cocktail_id:5d} : {cocktail['strIngredient']:20}")

            # Pause pour éviter de surcharger l'API
            time.sleep(0.2)

            # Affichage de progression tous les 50 IDs
            if cocktail_id % 50 == 0:
                current_progress = cocktail_id - start_id + 1
                total_to_process = end_id - start_id + 1
                progress_percent = (current_progress / total_to_process) * 100

                print(
                    f"📈 Progression: {progress_percent:5.1f}% | "
                    f"IDs traités: {current_progress:4d}/{total_to_process} | "
                    f"Cocktails trouvés: {len(found_cocktails):3d}"
                )

        except requests.exceptions.Timeout:
            print(f"⏰ Timeout avec ID {cocktail_id}")
        except requests.exceptions.ConnectionError:
            print(f"🔌 Erreur de connexion avec ID {cocktail_id}")
            time.sleep(2)  # Pause plus longue en cas de problème de connexion
        except Exception as e:
            print(f"❌ Erreur inattendue avec ID {cocktail_id}: {e}")

    # Sauvegarde de tous les cocktails dans un fichier consolidé
    if found_cocktails:
        consolidated_file = output_dir / "all_cocktails_consolidated.json"
        with open(consolidated_file, "w", encoding="utf-8") as f:
            json.dump({"drinks": found_cocktails}, f, indent=2, ensure_ascii=False)
        print(f"💾 Fichier consolidé sauvegardé : {consolidated_file}")

    # Sauvegarde des métadonnées et statistiques
    save_extraction_summary(
        output_dir,
        total_requests,
        successful_requests,
        len(found_cocktails),
        start_id,
        end_id,
        found_cocktails,
    )

    # Affichage du résumé final
    print_final_summary(total_requests, successful_requests, len(found_cocktails))


def save_extraction_summary(
    output_dir,
    total_requests,
    successful_requests,
    cocktails_found,
    start_id,
    end_id,
    cocktails_list,
):
    """Sauvegarde les métadonnées de l'extraction"""

    summary = {
        "extraction_info": {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "id_range_searched": f"{start_id}-{end_id}",
            "total_ids_tested": end_id - start_id + 1,
        },
        "statistics": {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "cocktails_found": cocktails_found,
            "success_rate": f"{(cocktails_found / total_requests) * 100:.2f}%",
            "coverage_rate": f"{(cocktails_found / (end_id - start_id + 1)) * 100:.2f}%",
        },
        "cocktails_summary": {
            "total_unique": len(cocktails_list),
            "categories": list(set([c.get("strCategory", "Unknown") for c in cocktails_list])),
            "glasses": list(set([c.get("strGlass", "Unknown") for c in cocktails_list])),
        },
    }

    summary_file = output_dir / "extraction_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Sauvegarde de la liste des IDs trouvés
    ids_file = output_dir / "found_cocktail_ids.json"
    found_ids = [cocktail["idDrink"] for cocktail in cocktails_list]
    with open(ids_file, "w", encoding="utf-8") as f:
        json.dump({"cocktail_ids": found_ids}, f, indent=2)


def print_final_summary(total_requests, successful_requests, cocktails_found):
    """Affiche un résumé final de l'extraction"""

    print("\n" + "=" * 60)
    print("🎉 EXTRACTION TERMINÉE !")
    print("=" * 60)
    print("📊 STATISTIQUES FINALES")
    print(f"   • Requêtes totales      : {total_requests}")
    print(f"   • Requêtes réussies     : {successful_requests}")
    print(f"   • Cocktails trouvés     : {cocktails_found}")
    print(f"   • Taux de réussite      : {(cocktails_found / total_requests) * 100:.2f}%")
    print("-" * 60)

    if cocktails_found > 0:
        print("💡 Conseils pour une extraction complète :")
        print("   • Les IDs de cocktails ne sont pas séquentiels")
        print("   • Certains IDs peuvent manquer dans la base de données")
        print("   • Vérifiez les fichiers dans extractAPI/extract_by_id/")
    else:
        print("❌ Aucun cocktail trouvé. Vérifiez :")
        print("   • Votre connexion Internet")
        print("   • L'accessibilité de l'API TheCocktailDB")
        print("   • La plage d'IDs spécifiée")


def check_api_availability():
    """Vérifie que l'API est accessible avant de commencer"""

    test_url = "https://www.thecocktaildb.com/api/json/v1/1/search.php?s=margarita"

    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            print("✅ API TheCocktailDB accessible")
            return True
        else:
            print("❌ API non accessible (code HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Impossible de joindre l'API : {e}")
        return False


if __name__ == "__main__":
    # Installation automatique de requests si nécessaire
    try:
        import requests
    except ImportError:
        print("📦 Installation de la bibliothèque requests...")
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests

        print("✅ Bibliothèque requests installée")

    # Vérification de l'API
    if check_api_availability():
        # Lancement de l'extraction
        start_time = time.time()
        extract_cocktails_by_id()
        end_time = time.time()

        print(f"⏱️  Temps d'exécution total : {end_time - start_time:.2f} secondes")
    else:
        print("❌ Extraction annulée - API non disponible")
