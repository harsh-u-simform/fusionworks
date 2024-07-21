from langchain_community.utilities.sql_database import SQLDatabase
from dotenv import load_dotenv
import os

class Database():

    def __init__(self) -> None:
        load_dotenv()
        self.db_user = os.getenv('MYSQL_DB_USER')
        self.db_password = os.getenv('MYSQL_DB_PASSWORD')
        self.db_host = os.getenv('MYSQL_DB_HOST')
        self.db_name = os.getenv('MYSQL_DB_NAME')

    def get_db(self, request):

        # db = SQLDatabase.from_uri(f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:5432/{self.db_name}")
        db = SQLDatabase.from_uri(f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}")

        return db
