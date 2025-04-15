import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

load_dotenv()

class DBConnection:
    _instance = None

    def __init__(self):
        if DBConnection._instance is not None:
            raise Exception("This class is a singleton!")
        self.connection = None

    @staticmethod
    def get_instance():
        """Get the singleton instance of DBConnection."""
        if DBConnection._instance is None:
            DBConnection._instance = DBConnection()
        return DBConnection._instance

    def connect(self):
        """Establish the connection to the database."""
        try:
            if not self.connection or self.connection.closed:
                self.connection = psycopg2.connect(
                    os.getenv('POSTGRES_URI'),
                    cursor_factory=RealDictCursor
                )
                print("🗄️  Database connection established successfully!")
        except Exception as e:
            print(f"⚠️ Error connecting to the database: {e}")
            self.connection = None

    def get_connection(self):
        """Ensure the connection is active and return it."""
        try:
            if self.connection.closed:
                self.connect()
        except AttributeError:
            self.connect()
        return self.connection
