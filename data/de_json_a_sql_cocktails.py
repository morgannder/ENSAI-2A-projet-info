import json


with open("extractAPI/all_cocktails_consolidated.json", "r", encoding="utf-8") as f:
    data = json.load(f)


insert_lines = []
for drink in data["drinks"]:
    # Échapper les caractères spéciaux pour SQL
    def escape_text(text):
        if text is None:
            return "NULL"
        # Remplacer les apostrophes par deux apostrophes (échappement SQL)
        text = text.replace("'", "''")
        # Échapper les backslashes
        text = text.replace("\\", "\\\\")
        # Remplacer les sauts de ligne par des espaces
        text = text.replace("\n", " ")
        # Nettoyer les autres caractères problématiques
        text = text.replace("\r", " ")
        return text.strip()

    id_drink = drink["idDrink"]
    name = escape_text(drink["strDrink"])
    category = escape_text(drink["strCategory"])
    alcoholic = escape_text(drink["strAlcoholic"])
    glass = escape_text(drink["strGlass"])
    instructions = escape_text(drink["strInstructions"])
    instructions_es = escape_text(drink.get("strInstructionsES"))
    instructions_de = escape_text(drink.get("strInstructionsDE"))
    instructions_fr = escape_text(drink.get("strInstructionsFR"))
    instructions_it = escape_text(drink.get("strInstructionsIT"))
    thumb = escape_text(drink["strDrinkThumb"])

    instructions_es = f"'{instructions_es}'" if instructions_es != "NULL" else "NULL"
    instructions_de = f"'{instructions_de}'" if instructions_de != "NULL" else "NULL"
    instructions_fr = f"'{instructions_fr}'" if instructions_fr != "NULL" else "NULL"
    instructions_it = f"'{instructions_it}'" if instructions_it != "NULL" else "NULL"

    insert_line = f"({id_drink}, '{name}', '{category}', '{alcoholic}', '{glass}', '{instructions}', {instructions_es}, {instructions_de}, {instructions_fr}, {instructions_it}, '{thumb}')"
    insert_lines.append(insert_line)


sql_content = "INSERT INTO cocktail(id_cocktail, nom, categorie, alcoolise, verre, instructions, instructions_es, instructions_de, instructions_fr, instructions_it, image_url) VALUES\n"


for i in range(0, len(insert_lines), 8):
    chunk = insert_lines[i : i + 8]
    sql_content += ",\n".join(chunk)
    if i + 8 < len(insert_lines):
        sql_content += ",\n"
    else:
        sql_content += ";"


with open("insert_cocktails.sql", "w", encoding="utf-8") as f:
    f.write(sql_content)

print("Fichier 'insert_cocktails.sql' généré avec succès!")
