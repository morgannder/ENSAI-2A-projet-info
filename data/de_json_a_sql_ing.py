import json


def clean_string(text):
    """Nettoie les chaînes de caractères pour les requêtes SQL"""
    if text is None:
        return ""
    return str(text).replace("'", "''")


def json_to_ingredients(json_file_path, sql_output_path):
    # Lire le fichier JSON
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(sql_output_path, "w", encoding="utf-8") as sql_file:
        sql_file.write("-- Insertions des ingrédients depuis le JSON\n\n")

        # Préparer les valeurs pour l'INSERT
        ingredient_values = []

        # Parcourir tous les ingrédients dans le tableau "drinks"
        for ingredient_data in data["drinks"]:
            id_ingredient = ingredient_data["idIngredient"]
            nom_ingredient = clean_string(ingredient_data["strIngredient"])
            desc_ingredient = clean_string(ingredient_data["strDescription"])

            ingredient_values.append(
                f"({id_ingredient}, '{nom_ingredient}', '{desc_ingredient}')"
            )

        # Écrire l'INSERT bulk
        if ingredient_values:
            sql_file.write(
                "INSERT INTO ingredient (id_ingredient, nom_ingredient, desc_ingredient) VALUES\n"
            )
            sql_file.write(",\n".join(ingredient_values))
            sql_file.write(";\n")

        sql_file.write(f"\n-- {len(ingredient_values)} ingrédients insérés\n")


# Utilisation
if __name__ == "__main__":
    json_file_path = (
        "extractAPI/all_ingredients_consolidated.json"  # Votre fichier JSON
    )
    sql_output_path = "insert_ingredients.sql"

    json_to_ingredients(json_file_path, sql_output_path)
    print(f"Fichier SQL pour les ingrédients généré : {sql_output_path}")
