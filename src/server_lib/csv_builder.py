from server_lib.session_record_manager import Record
from resource_manager import CONFIG
import os
from datetime import datetime
class CSVBuilder:
    def build(data : list[Record], session_id : str, researcher_id : str = None):

        path = os.path.join(CONFIG["server"]["temp_directory"], session_id)
        path = os.path.join(path, f"{researcher_id if researcher_id else 'anonymous'}_{datetime.now().strftime('%H%M%S_%Y%m%d')}.csv")
        sorted_seeds_records = {}
        keys = []
        for record in data:
            key = record._seed_id
            if key == None:
                key = "no_id"
            if not key in sorted_seeds_records:
                sorted_seeds_records[key] = []
            
            sorted_seeds_records[key].append(str(record._velocity))

        with open(path, "w") as file:
            for key in sorted_seeds_records:
                sorted_seeds_records[key].insert(0, key)
                file.write(f"{','.join(sorted_seeds_records[key])}\n")
        

        return path