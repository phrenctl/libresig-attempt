class InMemoryDatabase:
    def __init__(self):
        # For level 1 key: {field: value}
        self.database = {}
        # For level 4 backup storage:
        # To store all the backup timestamps for quick lookup of the latest 
        # backup before a restore timestamp
        self.backup_timestmps: list[int] = []
        # To store the actual backup database
        self.backup_states: list[dict] = []

    # Level 1
    def set(self, key, field, value):
        """
        The following implementation is sufficient for Level 1 and Level 2, 
        but will need to be modified for Level 3 to handle expiry times.
        """
        # if key not in self.database:
        #     self.database[key] = {}
        # self.database[key][field] = value
        # return ""
        
        # Implementation for Level 3:
        return self._set_internal(key, field, value, None)
    
    def get(self, key, field):
        if key not in self.database or field not in self.database[key]:
            return ""
        # Implementation for Level 1 and 2:
        # return self.database[key][field]
        
        # Implementation for Level 3:
        return self.database[key][field][0]

    def delete(self, key, field):
        if key not in self.database or field not in self.database[key]:
            return "false"
        del self.database[key][field]
        return "true"

    # Level 2
    def scan(self, key):
        if key not in self.database:
            return ""
        items = list(self.database[key].items())
        # Sort by field name in lexicographical order
        items.sort()  
        # Implementation for Level 1 and 2:
        # return ", ".join(f"{field}({value})" for field, value in items)

        # Implementation for Level 3:
        return ", ".join(f"{field}({value[0]})" for field, value in items)

    def scan_by_prefix(self, key, prefix):
        if key not in self.database:
            return ""
        items = [(field, value) for field, value in self.database[key].items() if field.startswith(prefix)]
        # Sort by field name in lexicographical order
        items.sort()  
        # Implementation for Level 1 and 2:
        # return ", ".join(f"{field}({value})" for field, value in items)
    
        # Implementation for Level 3:
        return ", ".join(f"{field}({value[0]})" for field, value in items)
    
    # Level 3
    # Helper function for setting a field with an expiry time
    def _set_internal(self, key, field, value, expiry):
        if key not in self.database:
            self.database[key] = {}
        self.database[key][field] = (value, expiry)
        return ""
    
    def set_at(self, key, field, value, timestamp):
        return self._set_internal(key, field, value, expiry=None)

    def set_at_with_ttl(self, key, field, value, timestamp, ttl):
        expiry = timestamp + ttl
        return self._set_internal(key, field, value, expiry)    

    def delete_at(self, key, field, timestamp):
        if key not in self.database or field not in self.database[key]:
            return "false"
        if not self._is_alive(key, field, timestamp):
            return "false"
        del self.database[key][field]
        return "true"

    def _is_alive(self, key, field, timestamp):
        if key not in self.database or field not in self.database[key]:
            return False
        value, expiry = self.database[key][field]
        if expiry is None:
            return True
        return timestamp < expiry
    
    def get_at(self, key, field, timestamp):
        if not self._is_alive(key, field, timestamp):
            return ""
        return self.database[key][field][0]

    def scan_at(self, key, timestamp):
        if key not in self.database:
            return ""
        items = []
        for field, (value, expiry) in self.database[key].items():
            if self._is_alive(key, field, timestamp):
                items.append((field, value))
        items.sort()
        return ", ".join(f"{field}({value})" for field, value in items)

    def scan_by_prefix_at(self, key, prefix, timestamp):
        if key not in self.database:
            return ""
        items = []
        for field, (value, expiry) in self.database[key].items():
            if field.startswith(prefix) and self._is_alive(key, field, timestamp):
                items.append((field, value))
        items.sort()
        return ", ".join(f"{field}({value})" for field, value in items)
    
    def backup(self, timestamp):
        # Create a backup of the current database state, including remaining lifespans for all records and fields
        # key: {field: (value, remaining_lifespan)}
        state = {}
        for key, field in self.database.items():
            for field, (value, expiry) in field.items():
                if self._is_alive(key, field, timestamp):
                    # Calculate remaining lifespan and save it in the backup
                    # None means no expiry
                    remaining_lifespan = expiry - timestamp if expiry is not None else None
                    # Save the key, field, value, and remaining lifespan in the backup state
                    if key not in state:
                        state[key] = {}
                    state[key][field] = (value, remaining_lifespan)
        self.backup_timestmps.append(timestamp)
        self.backup_states.append(state)
        # Return the number of non-empty non-expired records (the number of keys) in the database
        return str(len(state))
    
    def restore(self, timestamp, timestampToRestore):
        import bisect
        # Find the latest backup before timestampToRestore
        idx = bisect.bisect_right(self.backup_timestmps, timestampToRestore) - 1
        backup_state = self.backup_states[idx]
        # Restore the database state from the backup, recalculating expiry times based on the current timestamp
        self.database = {}
        for key, fields in backup_state.items():
            for field, (value, remaining_lifespan) in fields.items():
                expiry = None
                # If the field had a remaining lifespan in the backup, we need to recalculate its expiry time based on the current timestamp
                if remaining_lifespan is not None:
                    expiry = timestamp + remaining_lifespan
                self._set_internal(key, field, value, expiry)
        return ""