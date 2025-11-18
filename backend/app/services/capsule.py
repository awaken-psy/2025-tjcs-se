from database.orm.capsule import Capsule as CapsuleDB
from backend.app.database.config import get_db

class CapsuleManager:
    def __init__(self, capsule_db: CapsuleDB):
        self.db = get_db()

    def create_capsule(self):
        pass        
        
