"""
All your implementation code for the bank system simulation goes here.
"""
from collections import defaultdict

class FieldValue:
    def __init__(self, value, timestamp = None, ttl = None):
        self.value = value
        self.timestamp = timestamp
        self.ttl = ttl


class InMemoryDatabase:
    def __init__(self):
        self.records = defaultdict(dict)
    
    
    # ========== Level 1 Operations ==========
    def set(self,key, field, value):
        self.records[key][field] = FieldValue(value)
        return ""
    
    def get(self,key, field):
        if not self.records.get(key):
            return ""
        if not self.records.get(key).get(field):
            return ""

        return self.records.get(key).get(field).value


    def delete(self,key, field):
        if not self.records.get(key):
            return "false"
        if not self.records[key].get(field):
            return "false"

        del self.records[key][field]

        return "true"

    def scan_helper(self, field_map, prefix = False, prefixS = "" ):
        output_string = ""

        items_list = list(field_map.items())
        items_list = [(key, fv.value) for key, fv in items_list]
        items_list.sort(key = lambda x: x[0])

        for key, value in items_list:
            if prefix and key.startswith(prefixS):
                output_string += f"{key}({value}), "
            elif not prefix:
                output_string += f"{key}({value}), "

        output_string = output_string[:-2]

        return output_string

    
    # ========== Level 2 Operations ==========
    def scan(self, key):
        if not self.records.get(key):
            return ""
        return self.scan_helper(self.records.get(key))
        
    def scan_by_prefix(self, key, prefix):
        if not self.records.get(key):
            return ""

        return self.scan_helper(self.records.get(key), True, prefix)
        
    # ========== Level 3 Operations ==========
    def check_for_expired_fields(self, timestamp):

        fields_to_delete = []

        for key in self.records:
            for field in self.records[key]:

                if self.records[key][field].ttl and self.records[key][field].ttl <= timestamp:
                    fields_to_delete.append(field)

        for field in fields_to_delete:
            del self.records[key][field]


    def set_at(self, key, field, value, timestamp):
        self.check_for_expired_fields(timestamp)
        self.records[key][field] = FieldValue(value, timestamp)
        return ""
    
    def set_at_with_ttl(self, key, field, value, timestamp, ttl):
        self.check_for_expired_fields(timestamp)
        self.records[key][field] = FieldValue(value, timestamp, timestamp + ttl)
        return ""

    def delete_at(self, key, field, timestamp):
        self.check_for_expired_fields(timestamp)

        if not self.records.get(key):
            return "false"
        if not self.records[key].get(field):
            return "false"

        if self.records[key].get(field).timestamp >= timestamp:
            del self.records[key][field]
            return "true"

        return "false"

    def get_at(self, key, field, timestamp):
        self.check_for_expired_fields(timestamp)

        if not self.records.get(key):
            return ""
        if not self.records.get(key).get(field):
            return ""
        
        if self.records[key].get(field).timestamp <= timestamp:
            return self.records[key][field].value

        return ""
    
    def scan_at_helper(self, field_map, prefix = False, prefixS = "", timestamp = 0):
        output_string = ""

        items_list = list(field_map.items())
        items_list = [(key, fv.value) for key, fv in items_list if fv.timestamp <= timestamp]
        items_list.sort(key = lambda x: x[0])

        for key, value in items_list:
            if prefix and key.startswith(prefixS):
                output_string += f"{key}({value}), "
            elif not prefix:
                output_string += f"{key}({value}), "

        output_string = output_string[:-2]

        return output_string

    def scan_at(self, key, timestamp):
        self.check_for_expired_fields(timestamp)

        return self.scan_at_helper(self.records.get(key), timestamp = timestamp)


    def scan_by_prefix_at(self, key, prefix, timestamp):
        self.check_for_expired_fields(timestamp)

        return self.scan_at_helper(self.records.get(key), prefix = True, prefixS = prefix, timestamp = timestamp)

    # ========== Level 4 Operations ==========
    def backup(self, timestamp):

        records_left = 0
        for key in self.records:
            for field in self.records[key]:
                if self.records[key][field].timestamp >= timestamp:
                    if self.records[key][field].ttl and self.records[key][field].ttl > timestamp:
                        records_left += 1
                    elif not self.records[key][field].ttl:
                        records += 1

        return str(records_left)

    def restore(self, timestamp, timestampToRestore):
        pass