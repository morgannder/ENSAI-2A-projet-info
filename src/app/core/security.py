from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from service.utilisateur_service import UtilisateurService
from business_object.utilisateur import Utilisateur
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)
service_utilisateur = UtilisateurService()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> Utilisateur:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        utilisateur = service_utilisateur.trouver_par_id(user_id)
        if not utilisateur:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable")
        return utilisateur
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide")


def get_current_user_optional(token: str = Depends(oauth2_scheme)) -> Utilisateur | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        return service_utilisateur.trouver_par_id(user_id)
    except Exception:
        return None
