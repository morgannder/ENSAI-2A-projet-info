import json
import time
from pathlib import Path

import requests


def extraction_ingredient_par_id():
    """
    Extrait les ingredients via leur ID en parcourant une plage d'id (bruteforce) car les ids sont
    (a peu près) numérotés de 0 à 1000 de façon non ordonnée

    Parameters
    -----------
    None

    Return
    -----------
    None

    """
    # Fourchettes des ID que l'on cherche
    id_depart = 0
    id_fin = 1000

    # Configuration de l'arborescence
    chemin_de_sortie = Path("extractAPI/extract_ingredients")
    chemin_de_sortie.mkdir(parents=True, exist_ok=True)

    url_utilisee = "https://thecocktaildb.com/api/json/v1/1/lookup.php?iid="

    ingredients_trouves = []
    extractions_reussies = 0

    for ingredient_id in range(id_depart, id_fin + 1):
        url = f"{url_utilisee}{ingredient_id}"

        try:
            reponse = requests.get(url, timeout=10)

            if reponse.status_code == 200:
                data = reponse.json()

                if data.get("ingredients") is not None:
                    ingredient = data["ingredients"][0]
                    ingredients_trouves.append(ingredient)
                    extractions_reussies += 1

                    fichier_ingredient = (
                        chemin_de_sortie / f"ingredient_{ingredient_id}.json"
                    )
                    with open(fichier_ingredient, "w", encoding="utf-8") as f:
                        json.dump(ingredient, f, indent=2, ensure_ascii=False)

            time.sleep(0.2)

        except requests.exceptions.Timeout:
            print(f"Timeout, id:{ingredient_id}")
        except requests.exceptions.ConnectionError:
            print(f"Erreur de connexion,  id:{ingredient_id}")
        except Exception as e:
            print(f"Erreur id: {ingredient_id}, erreur: {e}")

    if ingredients_trouves:
        fichier_bdd = chemin_de_sortie / "total_ingredients.json"
        with open(fichier_bdd, "w", encoding="utf-8") as f:
            json.dump(
                {"ingredients": ingredients_trouves}, f, indent=2, ensure_ascii=False
            )

    print(f"\nNombre d'extraction(s) réussie(s): {extractions_reussies}")


def check_dispo_api():
    """
    Teste si l'API est disponible

    Parameters
    -----------
    None

    Return
    -----------
    Bool : True si l'API renvoie une réponse ce qui signifie qu'elle est disponible

    """

    url_test = "hhtps://thecocktaildb.com/api/json/v1/1/lookup.php?i=11007"

    try:
        reponse = requests.get(url_test, timeout=10)
        if reponse.status_code == 200:
            return True
        return False
    except Exception as e:
        print(f"Connexion impossible, erreur:{e}")


if __name__ == "__main__":
    if check_dispo_api:
        time.sleep(0.2)
        extraction_ingredient_par_id()
    else:
        print("API non disponible")
