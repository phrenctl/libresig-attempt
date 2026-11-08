"""
All your implementation code for the bank system simulation goes here.
"""
class InMemoryDatabase:
    def __init__(self):
        pass
    
    # ========== Level 1 Operations ==========
    def set(self,key, field, value):
        pass
    
    def get(self,key, field):
        pass

    def delete(self,key, field):
        pass
    
    # ========== Level 2 Operations ==========
    def scan(self, key):
        pass

    def scan_by_prefix(self, key, prefix):
        pass

    # ========== Level 3 Operations ==========
    def set_at(self, key, field, value, timestamp):
        pass

    def set_at_with_ttl(self, key, field, value, timestamp, ttl):
        pass

    def delete_at(self, key, field, timestamp):
        pass

    def get_at(self, key, field, timestamp):
        pass

    def scan_at(self, key, timestamp):
        pass

    def scan_by_prefix_at(self, key, prefix, timestamp):
        pass

    # ========== Level 4 Operations ==========
    def backup(self, timestamp):
        pass

    def restore(self, timestamp, timestampToRestore):
        pass