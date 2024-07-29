from server_lib.session_record_manager import Record
from resource_manager import CONFIG
import os
from datetime import datetime
class CSVBuilder:
    HEADER = "seed_id,velocity,error_margin,x_gap,z_gap\n"
    def build(data : list[Record], session_id : str, researcher_id : str = None):

        path = os.path.join(CONFIG["server"]["temp_directory"], session_id)
        path = os.path.join(path, f"{researcher_id if researcher_id else 'anonymous'}_{datetime.now().strftime('%H%M%S_%Y%m%d')}.csv")
        lines = [CSVBuilder.HEADER]
        for record in data:
            lines.append(record.to_csv_line())
        with open(path, "w") as file:
            file.writelines(lines)
    
        return path

    def append(file_path: str, data: Record):
        # Read the current contents of the file
        try:
            with open(file_path, "a") as file:
                ##Check if the file is empty
                file.write(data.to_csv_line())
        except FileNotFoundError:
            with open(file_path, "w") as file:
                file.write(CSVBuilder.HEADER)
                file.write(data.to_csv_line())


        



