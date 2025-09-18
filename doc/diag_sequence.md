# Diagramme de séquence : ajout d'un ingredient dans l'inventaire 

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

---
config:
  theme: redux-color
---
sequenceDiagram
  actor Utilisateur as Utilisateur
  participant Vue as Vue
  participant Service as InventaireService
  participant DAO as InventaireDAO
  participant DB as BDD
  Utilisateur ->> Vue: sélectionne l'ajout d'ingrédient
  Vue ->> Utilisateur: affiche liste d'ingrédients (suggestions)
  Utilisateur ->> Vue: saisit le nom "citron"
  Vue ->> Service: ajouterIngredient("citron", id_user)
  Service ->> DAO: obtenir_id_par_ingredient
  DAO ->> DB: recupère l'id_ingredient dans la table ingredient
  DB -->> Service: id_ingredient
  Service ->> DAO: cconsulter_inventaire
  DAO ->> DB: selectionne les ingredients de l'utilisateur
  DB -->> Service: liste id_ingredients
  alt id_ingredient déjà présent dans liste
      Service -->> Vue: Erreur: "Ingrédient déjà dans l'inventaire"
      Vue -->> Utilisateur: affichage message d'erreur
  else id_ingredient non présent
      Service ->> DAO: ajouterIngredient("citron", id_user)
      DAO ->> DB: ajout dans inventaire_Ingredient
      DB -->> DAO: OK
      DAO -->> Utilisateur: confirmation ajoutée
  end
```
