import hashlib
import re

from fastapi import HTTPException

REGEX_MDP = re.compile(
    r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[¤~²°£µ§;`!@#$%^&*(),.?\":{}|<>]).{8,}$"
)


def hash_password(password, sel=""):
    """Hachage du mot de passe"""
    password_bytes = password.encode("utf-8") + sel.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


def secu_mdp(mdp: str):
    """
    Vérifie si un mot de passe respecte les règles de sécurité via une seule regex.
    """
    if not REGEX_MDP.match(mdp):
        raise HTTPException(
            status_code=400,
            detail=(
                "Le mot de passe doit contenir : "
                "au moins 8 caractères, "
                "au moins une majuscule, "
                "au moins une minuscule, "
                "au moins un chiffre, "
                "et au moins un caractère    spécial."
            ),
        )
