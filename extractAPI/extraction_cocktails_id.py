import json
import time
from pathlib import Path

import requests


def extraction_cocktail_par_id():
    """
    Extrait les cocktails via leur ID en parcourant une plage d'id (bruteforce) car les ids sont
    (a peu près) numérotés de 11 000 à 18 000 et de 178 300 à 178 600 (donc non ordonnés)

    Parameters
    -----------
    None

    Return
    -----------
    None

    """
    # Fourchettes des ID que l'on cherche
    id_depart = 10000
    id_fin = 20000

    # Configuration de l'arborescence
    chemin_de_sortie = Path("extractAPI/extract_cocktails")
    chemin_de_sortie.mkdir(parents=True, exist_ok=True)

    url_utilisee = "https://thecocktaildb.com/api/json/v1/1/lookup.php?i="

    cocktails_trouves = []
    extractions_reussies = 0

    for cocktail_id in range(id_depart, id_fin + 1):
        url = f"{url_utilisee}{cocktail_id}"

        try:
            reponse = requests.get(url, timeout=10)

            if reponse.status_code == 200:
                data = reponse.json()

                if data.get("drinks") is not None:
                    cocktail = data["drinks"][0]
                    cocktails_trouves.append(cocktail)
                    extractions_reussies += 1

                    fichier_cocktail = chemin_de_sortie / f"cocktail_{cocktail_id}.json"
                    with open(fichier_cocktail, "w", encoding="utf-8") as f:
                        json.dump(cocktail, f, indent=2, ensure_ascii=False)

            # Temps d'attente pour pas se faire time out par l'API, si time.sleep(0.1) -> Time-out
            time.sleep(0.2)

        except requests.exceptions.Timeout:
            print(f"Timeout, id:{cocktail_id}")
        except requests.exceptions.ConnectionError:
            print(f"Erreur de connexion,  id:{cocktail_id}")
        except Exception as e:
            print(f"Erreur id: {cocktail_id}, erreur: {e}")
    if cocktails_trouves:
        fichier_bdd = chemin_de_sortie / "total_cocktails.json"
        with open(fichier_bdd, "w", encoding="utf-8") as f:
            json.dump({"cocktails": cocktails_trouves}, f, indent=2, ensure_ascii=False)

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
        extraction_cocktail_par_id()
    else:
        print("API non disponible")
