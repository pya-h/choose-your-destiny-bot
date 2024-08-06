from models.user_base import UserBase
from tools.mathematix import tz_today
from enum import Enum
from models.user_base import user_state_enum
from tools.mathematix import tz_today
from hugchat_interface import HugchatInterface


@user_state_enum()
class UserStates(Enum):
    '''Custom states of the user can be defined here'''
    NONE = 0
    PLAYING = 1


class User(UserBase):
    '''Extended version of the user model, varies by developer's need'''

    def __init__(self, chat_id, language: str = 'fa', manual_garbage_collection: bool = True, hugchat_interface: HugchatInterface = None) -> None:
        super().__init__(chat_id, language, manual_garbage_collection=manual_garbage_collection)
        self.hugchat = hugchat_interface

    @staticmethod
    def GarbageCollect():
        '''This account schematic always caches some users, in order to enhance the performance while accessing model data. So instead of accessing and reading database every single time, it reads from ram if there is that special user,
        As the ram memory is limited, this cached memory needs to be cleaned if the user has not interacted more than a special amount of time[GarbageCollectionInterval/2]'''
        now = tz_today()
        garbage = []
        for chat_id in User.Instances:
            if (now - User.Instances[chat_id].last_interaction).total_seconds() / 60 >= User.GarbageCollectionInterval / 2:
                garbage.append(chat_id)
        # because changing dict size in a loop on itself causes error,
        # we first collect redundant chat_id s and then delete them from the memory
        for g in garbage:
            del User.Instances[g]
    @staticmethod
    def Get(chat_id):
        if chat_id in User.Instances:
            User.Instances[chat_id].last_interaction = tz_today()
            return User.Instances[chat_id]
        
        # example of doing manual garbage collection
        if User.ManualGarbageCollection:
            User.GarbageCollect()
        try:
            row = User.Database().get(chat_id)
            if row:
                '''load database and create User from that and'''
                return User(row[0], row[1]) 
        except:
            pass
        return User(chat_id=chat_id).save()

    # continue overriding methods or defining new ones if required...