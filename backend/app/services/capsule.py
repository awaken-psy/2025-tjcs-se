from database.orm.capsule import Capsule as CapsuleDB
from app.database.database import get_db

class CapsuleManager:
    def __init__(self, capsule_db: CapsuleDB):
        self.db = get_db()

    def create_capsule(self):
        pass        
        
