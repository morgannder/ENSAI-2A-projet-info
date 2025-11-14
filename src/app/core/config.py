import os

import dotenv

from utils.reset_database import ResetDatabase

dotenv.load_dotenv()
os.environ["POSTGRES_SCHEMA"] = "projet_test"

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])

ResetDatabase().lancer(test_dao=False)
