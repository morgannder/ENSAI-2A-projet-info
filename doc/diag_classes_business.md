# Diagramme de classes orienté business (DAO et service )

Dans ce diagramme, nous avons  mis en avant la partie **business** de l'application.  
On y retrouve les **DAO** et les **services**.
L’idée ici, c’est de montrer quelles sont les **méthodes** que nous utilisons.  


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
   
    class VueAbstraite {
        +afficher()
        +choisir_menu()
    }

    class AccueilVue {
    }

    class ConnexionVue {
    }

    class MenuCocktailVue {
        +afficher_recette(idCocktail)
    }

    
    %% Services (Business Layer)
  
    class UtilisateurService {
        +creercompte(str...) :Utilisateur
        +deconnecter() : Bool
        +se_connecter(str,str) : Utilisateur
        +changer_mdp(str,str) : Utilisateur
        +changer_pseudo(str,str) : Utilisateur
    }

    class InventaireService {
        +ajouterIngredient(str)
        +supprimerIngredient(str)
        +consulterInventaire() : list[Ingredient]
    }

    class CocktailService {
        +rechercher_cocktail_par_nom(str) : list[Cocktail]
        +cocktail_complet() : list[Cocktail]
        +cocktail_partiel(int<3) : list[Cocktail]
    }

    
    %% DAO (Business Layer)
 
    class UtilisateurDAO {
        +creercompte(Utilisateur) :Utilisateur
        +deconnecter()
        +se_connecter(str,str) : Utilisateur
        +changer_mdp(str,str) : Utilisateur
        +changer_pseudo(str,str) : Utilisateur
    }

    class CocktailDAO {
        +rechercher_cocktail_par_nom(str) : list[Cocktail]
        +cocktail_complet() : list[Cocktail]
        +cocktail_partiel(int<3) : list[Cocktail]
    }

    class InventaireDAO {
        +ajouterIngredient(Ingredient)
        +supprimerIngredient(int)
        +consulterInventaire() : list[Ingredient]
    }

    
    VueAbstraite <|-- AccueilVue
    VueAbstraite <|-- ConnexionVue
    VueAbstraite <|-- MenuCocktailVue

    AccueilVue ..> CocktailService : appelle
    ConnexionVue ..> UtilisateurService : appelle
    MenuCocktailVue ..> CocktailService : appelle

    UtilisateurService ..> UtilisateurDAO : appelle
    CocktailService ..> CocktailDAO : appelle
    InventaireService ..> InventaireDAO : appelle

    UtilisateurService ..> InventaireService : utilise pour gérer l'inventaire de l'utilisateur
    CocktailService ..> InventaireService : consulte pour déterminer recette complète ou partielle lors de la recherche


```
