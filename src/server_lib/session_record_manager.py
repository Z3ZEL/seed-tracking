from uuid import UUID
from resource_manager import CONFIG as config
from server_lib.record import Record
from server_lib.memory_manager import MemoryManager

class SessionRecordManager:
    """
        The SessionRecordManager is a class that manages the records of a session.
        It is used to store the records of a session and to validate them.
    """
    def __init__(self, memory_manager : MemoryManager) -> None:
        self.session_records : dict[UUID, list[Record]] = {}
        self._linked_researchers : dict[UUID, str]= {}
        self._memory_manager = memory_manager

        


    def init_session(self, session_id : UUID, researcher_id : str = None):
        """
        Initializes a new session with the given session ID and optional researcher ID.

        Parameters:
            session_id (UUID): The unique identifier for the session.
            researcher_id (str, optional): The ID of the researcher associated with the session.

        Returns:
            None

        """
        self.session_records[session_id] = []
        if researcher_id:
            self._linked_researchers[session_id] = researcher_id
    def stop_session(self, session_id : UUID):
        """
        Removes the session record associated with the given session ID.

        Parameters:
        - session_id (UUID): The ID of the session to be stopped.

        """
        del self.session_records[session_id]
    def add_record(self, session_id : UUID,  record : Record):
        """
        Add a record to the session with the given session_id.

        Parameters:
        - session_id (UUID): The ID of the session to add the record to.
        - record (Record): The record to be added.
        """
        self.session_records[session_id].append(record)

    def validate_record(self, session_id : UUID):
        """
        - This method validates a session record by marking it as validated.
        - If the session record is associated with a researcher, it is also logged in the backup CSV.

        Parameters:
        - session_id (UUID): The ID of the session to validate.

        """
        if len(self.session_records[session_id]) == 0:
            return
        if not self.session_records[session_id][-1]._validated:
            self.session_records[session_id][-1]._validated = True
            ## Append record to backup csv only if it associated with a researcher
            if session_id in self._linked_researchers:
                self._memory_manager.log_record(str(session_id), self._linked_researchers[session_id], self.session_records[session_id][-1])
            


    def pop_record(self, session_id: UUID) -> Record:
        """
        Pop the last record from the session_records list for the given session_id.

        Parameters:
        - session_id (UUID): The ID of the session.

        Returns:
        - None: If the session_records list is empty or the last record is already validated.

        """
        if len(self.session_records[session_id]) == 0 or self.session_records[session_id][-1]._validated:
            return
        return self.session_records[session_id].pop(-1)

    def get_last_record(self, session_id : UUID) -> dict:
        """
        Retrieves the last record for a given session ID.
        Args:
            session_id (UUID): The ID of the session.
        Returns:
            dict: The last record as a dictionary, or None if no records exist for the session.
        """
        if len(self.session_records[session_id]) == 0:
            return None
        return self.session_records[session_id][-1].to_json()
    
    def get_linked_researcher(self, session_id : UUID) -> str | None :
        """
        Retrieves the linked researcher id for a given session ID. If 
        the session is a student session, retrieve None

        Parameters:
            session_id (UUID): The ID of the session.

        Returns:
            str | None: The linked researcher's name if found, None otherwise.
        """
        if session_id in self._linked_researchers:
            return self._linked_researchers[session_id]
        else:
            return None
    
    def get_records(self, session_id : UUID) -> list[Record]:
        """
            Retrieves the records associated with the given session ID.

            Args:
                session_id (UUID): The ID of the session.

            Returns:
                list[Record]: A list of records associated with the session ID. Returns None if no records are found.
        """ 
        if len(self.session_records[session_id]) == 0:
            return None
        return [ record for record in self.session_records[session_id]]


