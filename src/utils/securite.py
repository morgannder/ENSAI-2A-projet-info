import hashlib


def hash_password(password, sel=""):
    """Hachage du mot de passe"""
    password_bytes = password.encode("utf-8") + sel.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()

# securite.py
import re
from fastapi import HTTPException

def hash_password(password, sel=""):
    """Hachage du mot de passe"""
    password_bytes = password.encode("utf-8") + sel.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


def secu_mdp(mdp: str):
    """
    Vérifie si le mot de passe respecte les règles de sécurité :
    - au moins 8 caractères
    - au moins 1 majuscule
    - au moins 1 minuscule
    - au moins 1 chiffre
    - au moins 1 caractère spécial
    """
    if not mdp:
        raise HTTPException(status_code=400, detail="Le mot de passe ne peut pas être vide")
    if len(mdp) < 8:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 8 caractères")
    if not re.search(r"[A-Z]", mdp):
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins une majuscule")
    if not re.search(r"[a-z]", mdp):
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins une minuscule")
    if not re.search(r"[0-9]", mdp):
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins un chiffre")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", mdp):
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins un caractère spécial")
