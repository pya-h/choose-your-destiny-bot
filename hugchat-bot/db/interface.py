from db.interface_base import DatabaseInterfaceBase

class DatabaseInterface(DatabaseInterfaceBase):
    '''Implement your actual database here. This is the Actual one used in bot.'''
    _instance = None

    @staticmethod
    def Get():
        if not DatabaseInterface._instance:
            DatabaseInterface._instance = DatabaseInterface()
        return DatabaseInterface._instance

    def setup(self):
        '''Write the overriding version'''
    # continue
