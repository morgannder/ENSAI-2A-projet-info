import logging
from functools import wraps


class LogIndentation:
    """Pour indenter les logs lorsque l'on rentre dans une nouvelle méthode"""

    current_indentation = 0

    @classmethod
    def increase_indentation(cls):
        """Ajouter une indentation"""
        cls.current_indentation += 1

    @classmethod
    def decrease_indentation(cls):
        """Retirer une indentation"""
        if cls.current_indentation > 0:
            cls.current_indentation -= 1

    @classmethod
    def get_indentation(cls):
        """Obtenir l'indentation"""
        return "    " * cls.current_indentation


def log(func):
    """
    Décorateur pour logger automatiquement les appels de méthodes

    Affiche dans les logs :
    - L'appel de la méthode avec les paramètres
    - La sortie retournée
    - Gère l'indentation pour les appels imbriqués
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Utilise le logger du module appelant plutôt que __name__
        logger = logging.getLogger(func.__module__)

        LogIndentation.increase_indentation()
        indentation = LogIndentation.get_indentation()

        # Récupération des paramètres
        class_name = args[0].__class__.__name__ if args else ""
        method_name = func.__name__

        # Construction de la liste des arguments
        args_repr = []

        # Arguments positionnels (sauf self/cls)
        if args:
            args_repr.extend(repr(arg) for arg in args[1:])

        # Arguments nommés
        args_repr.extend(f"{k}={repr(v)}" for k, v in kwargs.items())

        # Masquage des mots de passe
        sensitive_keywords = [
            "password",
            "passwd",
            "pwd",
            "pass",
            "mot_de_passe",
            "mdp",
        ]
        for i, arg in enumerate(args_repr):
            for sensitive in sensitive_keywords:
                if sensitive in arg.lower():
                    args_repr[i] = "*****"
                    break

        signature = ", ".join(args_repr)

        # Log de début
        logger.info(f"{indentation}▶ {class_name}.{method_name}({signature})")

        try:
            result = func(*args, **kwargs)

            # Formatage du résultat
            if isinstance(result, list):
                if len(result) > 3:
                    result_str = f"[{', '.join(str(item) for item in result[:3])}...] ({len(result)} éléments)"
                else:
                    result_str = str(result)
            elif isinstance(result, dict):
                if len(result) > 3:
                    items = list(result.items())[:3]
                    result_str = f"{{{', '.join(f'{k}: {v}' for k, v in items)}...}} ({len(result)} éléments)"
                else:
                    result_str = str(result)
            elif isinstance(result, str) and len(result) > 50:
                result_str = f"'{result[:50]}...' ({len(result)} caractères)"
            elif result is None:
                result_str = "None"
            else:
                result_str = str(result)

            # Log de fin avec résultat
            logger.info(f"{indentation}✓ {class_name}.{method_name} → {result_str}")

            return result

        except Exception as e:
            # Log des erreurs
            logger.error(
                f"{indentation}✗ {class_name}.{method_name} → ERREUR: {str(e)}"
            )
            LogIndentation.decrease_indentation()
            raise
        finally:
            LogIndentation.decrease_indentation()

    return wrapper
