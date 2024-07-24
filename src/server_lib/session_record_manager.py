from uuid import UUID
from resource_manager import CONFIG as config

class Record:
    def __init__(self, velocity : float, error_margin : float, plots : list[str], seed_images : list[str], master_seed_number : int, slave_seed_number : int, seed_id : str = None) -> None:
        self._velocity : float = velocity
        self._error_margin : float = error_margin
        self._plots : list[str] = plots
        self._seed_images : list[str] = seed_images
        self._master_seed_number : int = master_seed_number
        self._slave_seed_number : int = slave_seed_number
        self._seed_id : str = seed_id
        self._validated : bool = False

    def to_json(self) -> dict:
        dict = self.__dict__ 
        ## Remove the validated key
        return {
            "velocity" : self._velocity,
            "error_margin" : self._error_margin,
            "plots" : self._plots,
            "seed_images" : self._seed_images,
            "seed_id" : self._seed_id,
            "slave_seed_number" : self._slave_seed_number,
            "master_seed_numver" : self._master_seed_number
        }
    
    def to_csv_line(self) -> str:
        '''
            Return the record in csv format
        '''
        return f'{self._seed_id if self._seed_id else "no_id"},{self._velocity}, {self._error_margin}\n'

class SessionRecordManager:
    def __init__(self, memory_manager) -> None:
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


