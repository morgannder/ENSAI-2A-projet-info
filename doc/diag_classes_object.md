# Diagramme de classes orienté objet

 
On décrit les **objets** avec leurs **attributs** et la manière dont ils sont reliés entre eux.  


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
        -mot_de_passe: String
        +nom: String
        +langue: String
        +adresse_mail: String
    }


    class Inventaire {
        +id_user: int
    }

    class Ingredient {
        +id_ingredient: int
        +nom_ingredient: String
        +description_ingredient: String

    }



    class Cocktail {
        +id_cocktail: int
        +nom: String
        +image: String
        +categorie: String
        +alcoolise: Boolean
        +instruction: String
        +type_verre : String
    }


    %% Relations

    Ingredient "*" --> "*" Cocktail
    Utilisateur "1" --> "1" Inventaire
    Ingredient "*" --> "*" Inventaire


```



