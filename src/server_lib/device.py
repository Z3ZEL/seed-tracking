from enum import Enum
from typing import List
from uuid import uuid4, UUID
from time import sleep
from server_lib import device_exception
from server_lib.session_record_manager import Record, SessionRecordManager
from server_lib.memory_manager import MemoryManager
from server_lib.csv_builder import CSVBuilder

from args import get_args_dict

if get_args_dict()["dev"]:
    from server_lib.record_launching_mock import RecordLauncher
else:
    from server_lib.record_launching import RecordLauncher

from resource_manager import CONFIG
class DeviceStatus(Enum):
    READY = 1
    BUSY = 2
    RECORDING = 3
    COMPUTING = 4
    ERROR = 5
    WAITING = 6




class Device:

    def __init__(self) -> None:
        self._status : DeviceStatus = DeviceStatus.WAITING
        self._sessions : List[UUID] = []
        self._records_manager = SessionRecordManager()
        self._memory_manager = MemoryManager(CONFIG["server"]["directory"], CONFIG["server"]["temp_directory"])
        self._last_error : device_exception.DeviceException = None

    @property
    def memory_manager(self):
        return self._memory_manager

    @property
    def current_session(self):
        return self._sessions[0] if len(self._sessions) > 0 else None

    def status(self, session_id: UUID = None) -> DeviceStatus:
       return self._status
    
    def change_current_session(self, new_current_session : UUID) :
        self._sessions.remvoe(new_current_session)
        self._sessions.insert(0, new_current_session)

    def change_status(self, status: DeviceStatus):
        if status == DeviceStatus.READY and len(self._sessions) <= 0:
            self._status = DeviceStatus.WAITING
        else:
            self._status = status

    def remove_session(self, session_id: UUID):
        self._sessions.remove(session_id)
        if len(self._sessions) == 0:
            self._status = DeviceStatus.WAITING

    def raise_error(self, error : device_exception.DeviceException):
        print(f"[ERROR] [{error.error_code}] {str(error)}")
        self._last_error = error
        self._status = DeviceStatus.ERROR

    def check_current_session(func):
        '''
            Decorator to check if the session is the current one, raise DeviceBusyException if not

            Use to protect the device to be operated by multiple sessions

        '''
        def inner(self, *args, **kwargs):
            if args[0] != None and args[0] not in self._sessions:
                raise device_exception.DeviceNoSessionException()
            session_id = args[0]
            if session_id  != self.current_session:
                print(f"[DEVICE] Session {session_id} is not the current session {self.current_session}")
                raise device_exception.DeviceBusyException()
            return func(self, *args, **kwargs)
        return inner

    def check_session(func):
        '''
            Decorator to check if the session id is valid
        '''
        def inner(self, *args, **kwargs):
            if args[0] not in self._sessions:
                raise device_exception.DeviceNoSessionException()
            return func(self, *args, **kwargs)
        return inner



    def check_status(status: DeviceStatus):
        def decorator(func):
            def inner(self, *args, **kwargs):
                if self._status != status:
                    raise device_exception.DeviceStateNotAllowed()
                return func(self, *args, **kwargs)
            return inner
        return decorator



    def start_session(self, researcher_id : str = None) -> str:
        '''
            Start a session with the device, return the session ID (uuid)

            This function is not protected everyone can start a session but only the current one can operate the device
        '''

        _session_id = uuid4()
        self._sessions.append(_session_id)

        if self._status == DeviceStatus.WAITING:
            self._status = DeviceStatus.READY

        #Records manager init
        self._records_manager.init_session(_session_id, researcher_id)

        return _session_id

    @check_session
    def stop_session(self, session_id : UUID):
        '''
            Stop a session with the device

            This function is not protected, everyone can stop its session
        '''

        self.remove_session(session_id)
        self._records_manager.stop_session(session_id)
        self._memory_manager.release_session(session_id)


    @check_session
    @check_status(DeviceStatus.READY)
    def start_record(self, session_id: UUID, duration: int, delay: int = 2, seed_id : str = None):
        '''
            Start a recording session, everyone who has a valid session can start a record.
        '''
        ## Change status
        self.change_status(DeviceStatus.RECORDING)

        ## Auto valid last record
        self._records_manager.validate_record(session_id)

        ## Adding recording and computing here thread based
        
        record_launcher = RecordLauncher(self, self._records_manager, self._memory_manager, session_id, 4, delay = delay, seed_id = seed_id)
        record_launcher.start()

        



    @check_session
    def get_record(self, session_id: UUID):
        '''
            Get the record of the last recording session
        '''
        record = self._records_manager.get_last_record(session_id)
        if record == None:
            raise device_exception.NoRecordFound()
        return record

    @check_session
    @check_status(DeviceStatus.READY)
    def validate_record(self, session_id: UUID, valid: bool):
        '''
            Validate the last record or invalidate it
        '''
        if not valid:
            self._records_manager.pop_reccord(session_id)
        else:
            self._records_manager.validate_record(session_id)




    @check_session
    def get_records_csv(self, session_id: UUID):
        '''
            Get all the records of the session
        '''
        records = self._records_manager.get_records(session_id)
        if records == None:
            raise device_exception.NoRecordFound()
        return CSVBuilder.build(records, str(session_id), researcher_id = self._records_manager.get_linked_researcher(session_id))

    @check_current_session
    @check_status(DeviceStatus.ERROR)
    def get_error_and_release(self, session_id: UUID) -> device_exception.DeviceException:
        self.change_status(DeviceStatus.READY)
        

        return {"error_code" : self._last_error.error_code, "error_message" : str(self._last_error)}









