import json

def generate_cocktail_ingredient_sql_advanced(ingredients_file, cocktails_file, output_sql_file):
    """
    Version améliorée avec gestion des erreurs et statistiques
    """
    
    try:
        # Charger les ingrédients
        with open(ingredients_file, 'r', encoding='utf-8') as f:
            ingredients_data = json.load(f)
        
        # Mapping nom d'ingrédient -> ID
        ingredient_name_to_id = {}
        for ingredient in ingredients_data['drinks']:
            clean_name = ingredient['strIngredient'].strip().lower()
            ingredient_name_to_id[clean_name] = ingredient['idIngredient']
        
        # Charger les cocktails
        with open(cocktails_file, 'r', encoding='utf-8') as f:
            cocktails_data = json.load(f)
        
        # Préparer la requête SQL
        sql_content = "INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, quantite) VALUES\n"
        
        values_list = []
        ingredients_not_found = set()
        
        # Statistiques
        total_associations = 0
        cocktails_processed = 0
        
        for cocktail in cocktails_data['drinks']:
            cocktail_id = cocktail['idDrink']
            cocktails_processed += 1
            
            for i in range(1, 16):
                ingredient_key = f'strIngredient{i}'
                measure_key = f'strMeasure{i}'
                
                if cocktail.get(ingredient_key) and cocktail[ingredient_key].strip():
                    ingredient_name = cocktail[ingredient_key].strip()
                    measure = cocktail.get(measure_key, '').strip() if cocktail.get(measure_key) else ''
                    
                    # Nettoyer le nom de l'ingrédient
                    clean_ingredient_name = ingredient_name.lower()
                    
                    # Chercher l'ID (avec quelques variations)
                    ingredient_id = None
                    if clean_ingredient_name in ingredient_name_to_id:
                        ingredient_id = ingredient_name_to_id[clean_ingredient_name]
                    else:
                        # Essayer sans espaces
                        no_space_name = clean_ingredient_name.replace(' ', '')
                        if no_space_name in ingredient_name_to_id:
                            ingredient_id = ingredient_name_to_id[no_space_name]
                        else:
                            ingredients_not_found.add(ingredient_name)
                    
                    if ingredient_id:
                        # Échapper les apostrophes
                        if measure:
                            measure = measure.replace("'", "''")
                        
                        quantite = f"'{measure}'" if measure else 'NULL'
                        values = f"({cocktail_id}, {ingredient_id}, {quantite})"
                        values_list.append(values)
                        total_associations += 1
        
        # Assembler la requête finale
        if values_list:
            sql_content += ",\n".join(values_list) + ";"
            
            # Écriture du fichier SQL
            with open(output_sql_file, 'w', encoding='utf-8') as sql_file:
                sql_file.write(sql_content)
            
            print("=== STATISTIQUES ===")
            print(f"Fichier SQL généré : {output_sql_file}")
            print(f"Nombre de cocktails traités : {cocktails_processed}")
            print(f"Nombre d'associations créées : {total_associations}")
            print(f"Nombre d'ingrédients non trouvés : {len(ingredients_not_found)}")
            
            if ingredients_not_found:
                print("\nIngrédients non trouvés :")
                for ing in sorted(ingredients_not_found):
                    print(f"  - {ing}")
        else:
            print("Aucune association trouvée !")
            
    except FileNotFoundError as e:
        print(f"Fichier non trouvé : {e}")
    except json.JSONDecodeError as e:
        print(f"Erreur de lecture JSON : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")

# Utilisation
if __name__ == "__main__":
    generate_cocktail_ingredient_sql_advanced(
        "extractAPI/all_ingredients_consolidated.json",
        "extractAPI/all_cocktails_consolidated.json",  # Votre fichier cocktails
        "cocktail_ingredient_insert.sql"
    )