from db.interface_base import DatabaseInterfaceBase
import sqlite3
from tools import manuwriter

class DatabaseInterface(DatabaseInterfaceBase):
    '''Implement your actual database here. This is the Actual one used in bot.'''
    _instance = None

    @staticmethod
    def Get():
        if not DatabaseInterface._instance:
            DatabaseInterface._instance = DatabaseInterface()
        return DatabaseInterface._instance

    def setup(self):
        connection = None
        try:
            connection = sqlite3.connect(self._name, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = connection.cursor()

            # check if the table users was created
            if not cursor.execute(f"SELECT name from sqlite_master WHERE name='{DatabaseInterfaceBase.TABLE_USERS}'").fetchone():
                query = f"CREATE TABLE {DatabaseInterfaceBase.TABLE_USERS} ({DatabaseInterfaceBase.USER_ID} INTEGER PRIMARY KEY," +\
                    f"{DatabaseInterfaceBase.USER_LANGUAGE} TEXT, {DatabaseInterfaceBase.USER_LAST_INTERACTION} DATE)"
                # create table user
                cursor.execute(query)
                manuwriter.log(f"{DatabaseInterfaceBase.TABLE_USERS} table created successfuly.", category_name='info')
            manuwriter.log("Database setup completed.", category_name='info')
            cursor.close()
            connection.close()
        except Exception as ex:
            if connection:
                connection.close()
            raise ex  # create custom exception for this
