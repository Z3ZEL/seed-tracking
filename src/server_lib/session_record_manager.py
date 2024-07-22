from uuid import UUID
import json

class Record:
    def __init__(self, velocity : float, error_margin : float, plots : list[str], seed_images : list[str]) -> None:
        self._velocity : float = velocity
        self._error_margin : float = error_margin
        self._plots : list[str] = plots
        self._seed_images : list[str] = seed_images
        self._validated : bool = False

    def to_json(self) -> dict:
        dict = self.__dict__ 
        ## Remove the validated key
        del dict['_validated']
        return dict

class SessionRecordManager:
    def __init__(self):
        self.session_records : dict[UUID, list[Record]] = {}

        


    def init_session(self, session_id : UUID):
        self.session_records[session_id] = []
    def stop_session(self, session_id : UUID):
        del self.session_records[session_id]
    def add_record(self, session_id : UUID,  record : Record):
        self.session_records[session_id].append(record)

    def validate_record(self, session_id : UUID):
        if len(self.session_records[session_id]) == 0:
            return
        self.session_records[session_id][-1]._validated = True
    def pop_reccord(self, session_id: UUID):
        if len(self.session_records[session_id]) == 0 or self.session_records[session_id][-1]._validated:
            return
        self.session_records[session_id].pop(-1)

    def get_last_record(self, session_id : UUID) -> dict:
        if len(self.session_records[session_id]) == 0:
            return None
        return self.session_records[session_id][-1].to_json()
    
    def get_records(self, session_id : UUID) -> list[Record]:
        if len(self.session_records[session_id]) == 0:
            return None
        return [ record for record in self.session_records[session_id]]


