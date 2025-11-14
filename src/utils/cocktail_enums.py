from typing import Literal

"""Types Literal pour les cocktails."""

# Type d'alcool
Alcool = Literal["Alcoholic", "Non alcoholic", "Optional Alcohol"]

# Choix du nombre d’ingrédients manquants pour la recherche partielle
Number = Literal["1", "2", "3", "4", "5"]

# Catégories de cocktails
Categories = Literal[
    "Beer",
    "Cocktail",
    "Cocoa",
    "Coffee / Tea",
    "Homemade Liqueur",
    "Ordinary Drink",
    "Other / Unknown",
    "Punch / Party Drink",
    "Shake",
    "Shot",
    "Soft Drink",
]

# Type de verres
Verres = Literal[
    "Balloon Glass",
    "Beer Glass",
    "Beer mug",
    "Beer pilsner",
    "Brandy snifter",
    "Champagne flute",
    "Champagne Flute",
    "Cocktail glass",
    "Cocktail Glass",
    "Coffee mug",
    "Coffee Mug",
    "Collins glass",
    "Collins Glass",
    "Copper Mug",
    "Cordial glass",
    "Coupe Glass",
    "Highball glass",
    "Highball Glass",
    "Hurricane glass",
    "Irish coffee cup",
    "Jar",
    "Margarita glass",
    "Margarita/Coupette glass",
    "Martini Glass",
    "Mason jar",
    "Nick and Nora Glass",
    "Old-fashioned glass",
    "Old-Fashioned glass",
    "Parfait glass",
    "Pint glass",
    "Pitcher",
    "Pousse cafe glass",
    "Punch bowl",
    "Punch Bowl",
    "Shot glass",
    "Shot Glass",
    "Whiskey Glass",
    "Whiskey sour glass",
    "White wine glass",
    "Wine Glass",
]
