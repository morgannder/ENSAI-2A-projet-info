import json
import time
from pathlib import Path

import requests


def extract_cocktail_data():
    # Créer le répertoire de destination
    output_dir = Path("src/extractAPI")
    output_dir.mkdir(parents=True, exist_ok=True)

    base_url = "https://www.thecocktaildb.com/api/json/v1/1/search.php?f="

    # Lettres de l'alphabet à traiter
    letters = [chr(i) for i in range(ord("a"), ord("z") + 1)]

    total_cocktails = 0
    successful_requests = 0

    print("Début de l'extraction des données cocktail...")
    print(f"Répertoire de sauvegarde : {output_dir.absolute()}")
    print("-" * 50)

    for letter in letters:
        url = f"{base_url}{letter}"
        filename = output_dir / f"cocktails_{letter}.json"

        try:
            print(f"Extraction de la lettre '{letter}'...", end=" ")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Vérifier si des cocktails sont présents
            if data["drinks"] is not None:
                cocktail_count = len(data["drinks"])
                total_cocktails += cocktail_count

                # Sauvegarder le fichier
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                successful_requests += 1
                print(f"✓ {cocktail_count} cocktails trouvés")

            else:
                # Sauvegarder même si aucun cocktail (pour conserver la structure)
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump({"drinks": None}, f, indent=2, ensure_ascii=False)
                print("✗ Aucun cocktail trouvé")

        except requests.exceptions.RequestException as e:
            print(f"✗ Erreur pour la lettre '{letter}': {e}")

        except Exception as e:
            print(f"✗ Erreur inattendue pour '{letter}': {e}")
        time.sleep(2)  # Pause pour éviter de surcharger le serveur

    # Créer un fichier de résumé
    summary = {
        "total_letters_processed": len(letters),
        "successful_requests": successful_requests,
        "total_cocktails_extracted": total_cocktails,
        "files_saved_in": str(output_dir.absolute()),
    }

    summary_file = output_dir / "extraction_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("-" * 50)
    print("Extraction terminée !")
    print(f"Lettres traitées : {len(letters)}")
    print(f"Requêtes réussies : {successful_requests}")
    print(f"Total cocktails extraits : {total_cocktails}")
    print(f"Fichiers sauvegardés dans : {output_dir.absolute()}")
    print(f"Résumé détaillé dans : {summary_file}")


# Version avec progression détaillée (alternative)
def extract_cocktail_data_with_progress():
    output_dir = Path("src/extractAPI")
    output_dir.mkdir(parents=True, exist_ok=True)

    base_url = "https://www.thecocktaildb.com/api/json/v1/1/search.php?f="
    letters = [chr(i) for i in range(ord("a"), ord("z") + 1)]

    results = {}

    print("🚀 Extraction des cocktails par lettre...")
    print(f"📁 Destination: {output_dir.absolute()}\n")

    for i, letter in enumerate(letters, 1):
        url = f"{base_url}{letter}"
        filename = output_dir / f"cocktails_{letter}.json"

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            cocktail_count = len(data["drinks"]) if data["drinks"] else 0

            # Sauvegarder le fichier
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            results[letter] = {
                "status": "success",
                "cocktail_count": cocktail_count,
                "file": str(filename),
            }

            print(
                f"[{i:2d}/{len(letters)}] {letter.upper()} : {cocktail_count:3d} cocktails"
            )

        except Exception as e:
            results[letter] = {
                "status": "error",
                "error": str(e),
                "file": str(filename),
            }
            print(f"[{i:2d}/{len(letters)}] {letter.upper()} : ERREUR - {e}")
        time.sleep(2)  # Pause pour éviter de surcharger le serveur

    # Sauvegarder les résultats détaillés
    summary_file = output_dir / "detailed_results.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Statistiques finales
    successful = [r for r in results.values() if r["status"] == "success"]
    total_cocktails = sum(r["cocktail_count"] for r in successful)

    print("\n✅ Extraction terminée !")
    print(f"📊 {len(successful)}/{len(letters)} lettres traitées avec succès")
    print(f"🍸 {total_cocktails} cocktails extraits au total")
    print(f"💾 Fichiers sauvegardés dans: {output_dir.absolute()}")


if __name__ == "__main__":
    # Installer requests si nécessaire
    try:
        import requests
    except ImportError:
        print("Installation de la bibliothèque requests...")
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests

    # Choisir la méthode d'extraction
    extract_cocktail_data_with_progress()  # Version avec progression détaillée
    # ou
    # extract_cocktail_data()  # Version simple
