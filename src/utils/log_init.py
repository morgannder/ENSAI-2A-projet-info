import logging
import logging.config
from pathlib import Path

import yaml


def initialiser_logs(nom_application="Application", config_path="logging_config.yml"):
    """
    Initialiser les logs à partir du fichier de config

    Parameters
    ----------
    nom_application : str
        Nom de l'application pour le header des logs
    config_path : str
        Chemin vers le fichier de configuration YAML
    """
    # Création du dossier logs à la racine si non existant
    Path("logs").mkdir(exist_ok=True)

    try:
        with open(config_path, encoding="utf-8") as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)
            logging.config.dictConfig(config)

        logging.info("-" * 50)
        logging.info(f"Lancement {nom_application}")
        logging.info("-" * 50)

    except FileNotFoundError:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)-8s - %(message)s",
            datefmt="%d/%m/%Y %H:%M:%S",
        )
        logging.warning(f"Fichier de configuration {config_path} non trouvé")


if __name__ == "__main__":
    initialiser_logs("Système de logs")
