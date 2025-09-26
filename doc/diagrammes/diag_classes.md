# Diagramme de classes

Ce diagramme est codé avec [mermaid](https://mermaid.js.org/syntax/classDiagram.html) :

* avantage : facile à coder
* inconvénient : on ne maîtrise pas bien l'affichage

Pour afficher ce diagramme dans VScode :

* à gauche aller dans **Extensions** (ou CTRL + SHIFT + X)
* rechercher `mermaid`

  * installer l'extension **Markdown Preview Mermaid Support**
* revenir sur ce fichier

  * faire **CTRL + K**, puis **V**

```mermaid
classDiagram
    class Utilisateur {
        +id_user: int
        +age: int
        +mot_de_passe: String
        +nom: String
        +langue: String
    }

    class Inventaire {
        +id_user: int
        +ajouterIngredient(nom_ingredient)
        +supprimerIngredient(nom_ingredient)
        +consulterInventaire(): list[Ingredient]
    }

    class Ingredient {
        +id_ingredient: int
        +nom_ingredient: String
    }

    class Cocktail {
        +id_cocktail: int
        +nom: String
        +categorie: String
        +alcoolise: Boolean
        +Search(): list[Cocktail]
        +cocktail_complet(): list[Cocktail]
        +cocktail_partiel(int<3): list[Cocktail]
    }

    %% Classe de jointure Inventaire - Ingredient
    class InventaireIngredient {
        id_user, id_ingredient
    }

    %% Classe de jointure Cocktail - Ingredient
    class CocktailIngredient {
         id_cocktail, id_ingredient
    }

    %% Relations
    Utilisateur "1" --> "1" Inventaire
    Inventaire "1" --> "*" InventaireIngredient
    Ingredient "1" --> "*" InventaireIngredient

    Cocktail "1" --> "*" CocktailIngredient
    Ingredient "1" --> "*" CocktailIngredient

```
