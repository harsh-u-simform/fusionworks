from langchain_community.utilities.sql_database import SQLDatabase

class Database():

    def __init__(self) -> None:
        self.db_user = 'sql12720708'
        self.db_password = '9GiP3RW9Js'
        self.db_host = 'sql12.freemysqlhosting.net'
        self.db_name = 'sql12720708'

    def get_db(self, request):

        db = SQLDatabase.from_uri(f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}")

        # print(db.dialect)
        # print(db.get_usable_table_names())
        # print(db.table_info)

        return db