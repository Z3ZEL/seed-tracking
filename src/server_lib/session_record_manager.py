from uuid import UUID
from resource_manager import CONFIG as config
from server_lib.record import Record
from server_lib.memory_manager import MemoryManager

class SessionRecordManager:
    def __init__(self, memory_manager : MemoryManager) -> None:
        self.session_records : dict[UUID, list[Record]] = {}
        self._linked_researchers : dict[UUID, str]= {}
        self._memory_manager = memory_manager

        


    def init_session(self, session_id : UUID, researcher_id : str = None):
        self.session_records[session_id] = []
        if researcher_id:
            self._linked_researchers[session_id] = researcher_id
    def stop_session(self, session_id : UUID):
        del self.session_records[session_id]
    def add_record(self, session_id : UUID,  record : Record):
        self.session_records[session_id].append(record)

    def validate_record(self, session_id : UUID):
        if len(self.session_records[session_id]) == 0:
            return
        if not self.session_records[session_id][-1]._validated:
            self.session_records[session_id][-1]._validated = True
            ## Append record to backup csv only if it associated with a researcher
            if session_id in self._linked_researchers:
                self._memory_manager.log_record(str(session_id), self._linked_researchers[session_id], self.session_records[session_id][-1])
            


    def pop_reccord(self, session_id: UUID):
        if len(self.session_records[session_id]) == 0 or self.session_records[session_id][-1]._validated:
            return
        self.session_records[session_id].pop(-1)

    def get_last_record(self, session_id : UUID) -> dict:
        if len(self.session_records[session_id]) == 0:
            return None
        return self.session_records[session_id][-1].to_json()
    
    def get_linked_researcher(self, session_id : UUID) -> str | None :
        if session_id in self._linked_researchers:
            return self._linked_researchers[session_id]
        else:
            return None
    
    def get_records(self, session_id : UUID) -> list[Record]:
        if len(self.session_records[session_id]) == 0:
            return None
        return [ record for record in self.session_records[session_id]]


