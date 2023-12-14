from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import json
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
import time


class CassandraDatabase:
    Conversations = dict()

    def __init__(self, token='adventures-token.json', bundle='secure-connect-adventures.zip', astra_db_keyspace='adventures_database') -> None:
        self.token = token
        self.bundle = bundle
        self.astra_db_keyspace = astra_db_keyspace
        self.messages_history = None
        self.chats_history = None
        self.cluster = None
        self.session = None

    def connect(self, chat_id):
        # This secure connect bundle is autogenerated when you download your SCB,
        # if yours is different update the file name below
        cloud_config = {
            'secure_connect_bundle': self.bundle
        }

        # This token JSON file is autogenerated when you download your token,
        # if yours is different update the file name below
        with open(self.token) as f:
            secrets = json.load(f)

        CLIENT_ID = secrets["clientId"]
        CLIENT_SECRET = secrets["secret"]

        auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
        self.cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
        self.session = self.cluster.connect()
        self.create_new_conversation(chat_id=chat_id)
        row = self.session.execute("select release_version from system.local").one()
        CassandraDatabase.Conversations[chat_id] = self
        return row[0] if row else None


    def create_new_conversation(self, chat_id, session_id=f'sh_{time.time()}', clean_after_secs=3600):
        # save session id and conversion id to avoid same ids
        self.messages_history = CassandraChatMessageHistory(
            session_id=session_id,
            session=self.session,
            ttl_seconds=clean_after_secs,
            keyspace=self.astra_db_keyspace
        )
        self.messages_history.clear()
        self.chats_history = ConversationBufferMemory(
            memory_key=chat_id,
            chat_memory=self.messages_history
        )

        return self.chats_history
