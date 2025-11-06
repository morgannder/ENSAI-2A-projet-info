import os
import dotenv
from datetime import timedelta
from utils.reset_database import ResetDatabase

dotenv.load_dotenv()
os.environ["POSTGRES_SCHEMA"] = "projet_test_dao"

SECRET_KEY = "sssecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60000


ResetDatabase().lancer(test_dao=True)
