import json


def ajoutcle():
    with open("extractAPI/all_cocktails_consolidated.json", "r", encoding="utf-8") as file:
        data = json.load(file)

        for j in range(0, 636):
            templistingredient = []
            templistmesure = []
            for i in range(1, 16):
                if data["drinks"][j][f"strIngredient{i}"]:
                    templistingredient.append(data["drinks"][j][f"strIngredient{i}"])
                    templistmesure.append(data["drinks"][j][f"strMeasure{i}"])
            data["drinks"][j]["listIngredients"] = templistingredient
            data["drinks"][j]["listMesures"] = templistmesure
    with open("extractAPI/all_cocktails_consolidated.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ajoutcle()


def reindicage_cocktail():
    with open("extractAPI/all_cocktails_consolidated.json", "r", encoding="utf-8") as file:
        data = json.load(file)

        for j in range(0, 636):
            data["drinks"][j]["idDrink"] = j
    with open("extractAPI/all_cocktails_consolidated.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# reindicage_cocktail()


def reindicage_ingredient():
    with open("extractAPI/all_ingredients_consolidated.json", "r", encoding="utf-8") as file:
        data = json.load(file)

        for j in range(0, 489):
            data["drinks"][j]["idIngredient"] = j
        del data["drinks"][j]["idIngredients"]
    with open("extractAPI/all_ingredients_consolidated.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# reindicage_ingredient()


def suppressioncleinutiles():
    with open("extractAPI/all_cocktails_consolidated.json", "r", encoding="utf-8") as file:
        data = json.load(file)

        for j in range(0, 636):
            for i in range(13, 16):
                del data["drinks"][j][f"strIngredient{i}"]
                del data["drinks"][j][f"strMeasure{i}"]
            del data["drinks"][j]["strDrinkAlternate"]
            del data["drinks"][j]["strTags"]
            del data["drinks"][j]["strVideo"]
            del data["drinks"][j]["strIBA"]
            del data["drinks"][j]["strInstructionsZH-HANS"]
            del data["drinks"][j]["strInstructionsZH-HANT"]
            del data["drinks"][j]["strImageSource"]
            del data["drinks"][j]["strImageAttribution"]
            del data["drinks"][j]["strCreativeCommonsConfirmed"]
            del data["drinks"][j]["dateModified"]
            del data["drinks"][j]["listIngredients"]
            del data["drinks"][j]["listMesures"]

    with open("extractAPI/all_cocktails_consolidated.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# suppressioncleinutiles()
