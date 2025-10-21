# service/inventaire_service.py
from typing import List, Optional
import logging

from business_object.ingredient import Ingredient
from dao.inventaire_dao import InventaireDao
from utils.log_decorator import log


class InventaireService:
    """Classe contenant les méthodes de service pour l'inventaire"""

    @log
    def lister_suggestion_ingredient(self, id_utilisateur) -> List[Ingredient]:
          """  ???????"""

    @log
    def ajouter_ingredient(self, nom_ingredient: Optional[str] = None, id_ingredient: Optional[int] = None) -> bool:
        """
        Créer un ingrédient dans l'inventaire global si un nom est fourni.
        Si seul un id est fourni (depuis des suggestions), aucune association utilisateur n'est faite ici.
        """
        try:
            dao = InventaireDao()

            # Création d'un nouvel ingrédient global par nom
            if isinstance(nom_ingredient, str) and nom_ingredient.strip():
                ing = Ingredient(
                    id_ingredient=None,
                    nom_ingredient=nom_ingredient.strip(),
                    desc_ingredient=None,
                )
                ok = dao.creer_ingredient(ing)
                if not ok:
                    logging.info("Échec de création de l'ingrédient '%s'.", nom_ingredient)
                return ok

            # Si on reçoit seulement un id_ingredient (issu d'une suggestion),
            # sans notion d'utilisateur ici, on ne fait rien (pas d'association côté service).
            if id_ingredient is not None:
                logging.info(
                    "Aucune action réalisée pour id_ingredient=%s (pas d'association utilisateur dans ce service).",
                    id_ingredient,
                )
                return False

            logging.info("Paramètres insuffisants pour ajouter_ingredient (ni nom, ni id).")
            return False

        except Exception as e:
            logging.exception("Erreur ajouter_ingredient: %s", e)
            return False

    @log
    def supprimer_ingredient(self, id_ingredient) -> bool:
        """
        Supprimer un ingrédient de l'inventaire global.
        """
        try:
            if not isinstance(id_ingredient, int):
                return False
            ok = InventaireDao().supprimer_ingredient(id_ingredient)
            if not ok:
                logging.info("Suppression échouée pour id_ingredient=%s.", id_ingredient)
            return ok
        except Exception as e:
            logging.exception("Erreur supprimer_ingredient: %s", e)
            return False

    @log
    def consulter_inventaire(self, id_utilisateur) -> list[Ingredient]:
        """
        Consulter tous les ingrédients de l'inventaire d'un utilisateur.
        """
        try:
            if not isinstance(id_utilisateur, int):
                return []
            return InventaireDao().consulter_inventaire(id_utilisateur)
        except Exception as e:
            logging.exception("Erreur consulter_inventaire: %s", e)
            return []
