from dotenv import load_dotenv
import os

load_dotenv()
PSQL_URL = os.getenv('PSQL_URL')
ENC_TABLE = os.getenv('ENC_TABLE')
HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))