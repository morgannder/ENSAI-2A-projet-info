# Diagramme d'écran

# Menu princpal visiteur
    - Se Connecter:                                             -> #Connexion
    - Créer un compte:                                          -> #Création de compte
    - Rechercher un cocktail:                                   -> #Recherche cocktail
    - Quitter l'application                                     -> exit

# Connexion
    - Identifiant: ->  Mot de passe:                            -> #Menu principal utilisateur
    - Retour:                                                   -> #Menu principal visiteur

# Menu princpal Utilisateur (personne connectée)
    - Rechercher une recette réalisable:                        -> #Recherche réalisable
    - Rechercher un cocktail:                                   -> #Recherche cocktail
    - Accès à l'inventaire:                                     -> #Inventaire
    - Paramètres:                                               -> #Paramètres

# Paramètres
    - Supprimer mon compte:                                     -> #Suppression de compte
    - Changer pseudo: -> nouveau pseudo                         -> /Booléen validation
    - Changer mdp: -> ancien mdp -> nouveau mdp                 -> /Booléen validation
    - Se déconnecter:                                           -> #Menu principal visiteur
    - Quitter l'application                                     -> exit
    - Retour:                                                   -> #Menu principal utilisateur


# Création de compte
    - Identifiant: -> Mail -> Mot de passe -> Age -> Langue     -> #Menu principal visiteur
    - Retour:                                                   -> #Menu principal visiteur

# Suppression de compte
    - Veuillez rentrer "CONFIRMER" afin de
        supprimer votre compte:                                 -> #Menu principal visiteur
    - Annuler:                                                  -> #Menu principal visiteur

# Recherche cocktail
    - Veuillez entrer le nom du cocktail:                       -> /Affichage Cocktail
    - Retour:                                                   -> #Menu principal utilisateur/visiteur

# Recherche réalisable
    - Cocktails réalisables dès maintenant:                     -> /Affichage Cocktail
    - Cocktails presque réalisables: -> nb ingrédients manquant:-> /Affichage Cocktail
    - Retour:                                                   -> #Menu principal utilisateur

# Inventaire
    - Voir inventaire:                                          -> /Affichage inventaire
    - Ajouter stock: -> Ingrédient                              -> /Booléen validation
    - Supprimer stock: -> Ingrédient                            -> /Booléen validation
    - Retour:                                                   -> #Menu principal utilisateur
