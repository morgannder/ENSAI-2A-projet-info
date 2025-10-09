DROP TABLE IF EXISTS inventaire_ingredient CASCADE ;
DROP TABLE IF EXISTS cocktail_ingredient CASCADE ;
DROP TABLE IF EXISTS cocktail CASCADE ;
DROP TABLE IF EXISTS ingredient CASCADE ;
DROP TABLE IF EXISTS utilisateur CASCADE ;


-----------------------------------------------------
-- Utilisateur
-----------------------------------------------------
CREATE TABLE utilisateur(
    id_utilisateur   SERIAL PRIMARY KEY,
    pseudo       VARCHAR(30) UNIQUE,
    mdp          VARCHAR(256),
    age          INTEGER,
    langue       VARCHAR(50),
    est_majeur  BOOLEAN
);


-----------------------------------------------------
-- Cocktail
-----------------------------------------------------
CREATE TABLE cocktail (
    id_cocktail  SERIAL PRIMARY KEY,
    nom_cocktail       VARCHAR(100),
    categorie        VARCHAR(100),
    alcool VARCHAR(100),
    image_url VARCHAR(256),
    verre VARCHAR(100),
    instructions TEXT,
    instructions_de TEXT,
    instructions_es TEXT,
    instructions_fr TEXT,
    instructions_it TEXT
);

-----------------------------------------------------
-- Ingredient
-----------------------------------------------------
CREATE TABLE ingredient (
    id_ingredient   SERIAL PRIMARY KEY,
    nom_ingredient       VARCHAR(30),
    desc_ingredient         TEXT
);


-----------------------------------------------------
-- Inventaire_ingredient
-----------------------------------------------------
CREATE TABLE inventaire_ingredient (
    id_utilisateur  INT NOT NULL,
    id_ingredient   INT NOT NULL,
    PRIMARY KEY (id_utilisateur, id_ingredient),
    CONSTRAINT fk_utilisateur FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur),
    CONSTRAINT fk_ingredient FOREIGN KEY (id_ingredient) REFERENCES ingredient(id_ingredient)
);


-----------------------------------------------------
-- Cocktail_ingredient
-----------------------------------------------------
CREATE TABLE cocktail_ingredient (
    id_cocktail  INT NOT NULL,
    id_ingredient   INT NOT NULL,
    quantite VARCHAR(50),
    PRIMARY KEY (id_cocktail, id_ingredient),
    CONSTRAINT fk_cocktail 
        FOREIGN KEY (id_cocktail) REFERENCES cocktail(id_cocktail),
    CONSTRAINT fk_ingredient 
        FOREIGN KEY (id_ingredient) REFERENCES ingredient(id_ingredient)
);
