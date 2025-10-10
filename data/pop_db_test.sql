INSERT INTO utilisateur(id_utilisateur, pseudo, mdp, age, langue, est_majeur) VALUES
(1, 'admin',      '0000',     1,      'Français',      false),
(2, 'a',             'a',     20,     'Français',      true),
(3, 'John',    '1234',        20,     'English',       true),
(4, 'batricia',   '9876',     15,     'Italiano',      false),
(5, 'Gilbert',     'abcd',    23,     'Deutsch',       true),
(6, 'miguel',    'toto',      11,     'Español',       false),
(7, 'junior',     'aaaa',     35,     'Deutsch',       true),
(8, 'Senior',     'jsp',      35,     'Deutsch',       true)
;


INSERT INTO cocktail(id_cocktail, nom_cocktail, categorie, alcool, verre, instructions, instructions_es, instructions_de, instructions_fr, instructions_it, image_url) VALUES
(0, 'Mojito', 'Cocktail', 'Alcoholic', 'Highball glass', 'Muddle mint leaves with sugar and lime juice. Add a splash of soda water and fill the glass with cracked ice. Pour the rum and top with soda water. Garnish and serve with straw.', 'Mezcle las hojas de menta con el azúcar y el zumo de lima. Añada un chorrito de soda y llene el vaso con hielo picado. Verter el ron y completar con soda. Decorar y servir con pajita.', 'Minzblätter mit Zucker und Limettensaft verrühren. Füge einen Spritzer Sodawasser hinzu und fülle das Glas mit gebrochenem Eis. Den Rum eingießen und mit Sodawasser übergießen. Garnieren und mit einem Strohhalm servieren.', 'Mélanger les feuilles de menthe avec le sucre et le jus de citron vert. Ajoutez un filet d''eau gazeuse et remplissez le verre de glace concassée. Verser le rhum et compléter avec de l''eau gazeuse. Décorer et servir avec une paille.', 'Pestare le foglie di menta con lo zucchero e il succo di lime.  Aggiungere una spruzzata di acqua di seltz e riempi il bicchiere con ghiaccio tritato.  Versare il rum e riempire con acqua di seltz.  Guarnire con una fetta di lime, servire con una cannuccia.', 'https://www.thecocktaildb.com/images/media/drink/metwgh1606770327.jpg'),
(1, 'Old Fashioned', 'Cocktail', 'Alcoholic', 'Old-fashioned glass', 'Place sugar cube in old fashioned glass and saturate with bitters, add a dash of plain water. Muddle until dissolved.  Fill the glass with ice cubes and add whiskey.    Garnish with orange twist, and a cocktail cherry.', 'Ponga el terrón de azúcar en un vaso old fashioned y úntelo con el amargo, añada un chorrito de agua. Mezcle hasta que se disuelva.  Llene el vaso con cubitos de hielo y añada whisky.    Decorar con un twist de naranja y una cereza de cóctel.', 'Zuckerwürfel in ein old fashioned Glas geben und mit Bitterstoff sättigen, einen Schuss Wasser hinzufügen. Vermischen, bis sie sich auflösen.', 'Placer un morceau de sucre dans un verre à l''ancienne et l''imbiber d''amers, ajouter un trait d''eau plate. Mélanger jusqu''à dissolution.  Remplir le verre de glaçons et ajouter le whisky.    Garnir d''un zeste d''orange et d''une cerise à cocktail.', 'Mettere la zolletta di zucchero nel bicchiere vecchio stile e saturare con il bitter, aggiungere un goccio di acqua naturale.  Pestare finché non si scioglie.  Riempi il bicchiere con cubetti di ghiaccio e aggiungi il whisky.  Guarnire con una scorza d''arancia e una ciliegina al maraschino.', 'https://www.thecocktaildb.com/images/media/drink/vrwquq1478252802.jpg'),
(2, 'Long Island Tea', 'Ordinary Drink', 'Alcoholic', 'Highball glass', 'Combine all ingredients (except cola) and pour over ice in a highball glass. Add the splash of cola for color. Decorate with a slice of lemon and serve.', 'Mezcle todos los ingredientes (excepto el refresco de cola) y viértalos sobre hielo en un vaso highball. Añada el chorrito de cola para darle color. Decore con una rodaja de limón y sirva.', 'Alle Zutaten (außer Cola) mischen und in einem Highball-Glas über Eis gießen. Füge einen Spritzer Cola hinzu, um Farbe zu erhalten. Mit einer Scheibe Zitrone dekorieren und servieren.', 'Mélanger tous les ingrédients (sauf le cola) et verser sur de la glace dans un verre highball. Ajoutez la goutte de cola pour donner de la couleur. Décorer avec une tranche de citron et servir.', 'Unisci tutti gli ingredienti (tranne la cola) e versa il ghiaccio in un bicchiere highball. Aggiungi la spruzzata di cola per il colore. Decorare con una fetta di limone e servire.', 'https://www.thecocktaildb.com/images/media/drink/nkwr4c1606770558.jpg')
;

INSERT INTO ingredient (id_ingredient, nom_ingredient, desc_ingredient) VALUES
(1, 'Gin', 'desc'),
(3, 'Tequila', 'desc'),
(18, 'Angostura Bitters', 'desc'),
(65, 'Bourbon', 'desc'),
(105, 'Coca-cola', 'desc'),
(240, 'lemon', 'desc'),
(244, 'Light Rum', 'desc'),
(251, 'Lime', 'desc'),
(273, 'Mint', 'desc'),
(361, 'Soda Water', 'desc'),
(379, 'Sugar', 'desc'),
(408, 'Water', 'desc')
;


INSERT INTO cocktail_ingredient (id_cocktail, id_ingredient, quantite) VALUES
(0, 244, '2-3 oz'),
(0, 251, 'Juice of 1'),
(0, 379, '2 tsp'),
(0, 273, '2-4'),
(0, 361, NULL),
(1, 65, '4.5 cL'),
(1, 18, '2 dashes'),
(1, 379, '1 cube'),
(1, 408, 'dash'),
(2, 244, '1/2 oz'),
(2, 1, '1/2 oz'),
(2, 3, '1/2 oz'),
(2, 240, 'Juice of 1/2'),
(2, 105, '1 splash')
;

INSERT INTO inventaire_ingredient(id_utilisateur, id_ingredient) VALUES
(3, 244),
(3, 251),
(3, 379),
(3, 273),
(3,361),
(3, 65),
(3, 18),
(3, 379),
(5, 244),
(5, 251),
(6, 244),
(6, 251),
(6, 379),
(6, 273),
(6, 65),
(6, 18),
(6, 379),


();