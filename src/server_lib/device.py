from enum import Enum
from typing import List
from uuid import uuid4, UUID
from time import sleep
from server_lib import device_exception
from server_lib.record import Record
from server_lib.session_record_manager import SessionRecordManager
from server_lib.memory_manager import MemoryManager
from server_lib.csv_builder import CSVBuilder

from args import get_args_dict

if get_args_dict()["dev"] and "mock" in get_args_dict()["dev"]:
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
        self._memory_manager = MemoryManager(CONFIG["server"]["directory"], CONFIG["server"]["temp_directory"])
        self._records_manager = SessionRecordManager(self._memory_manager)
        self._last_error : device_exception.DeviceException = None
        self._current_job : RecordLauncher = None

    @property
    def memory_manager(self):
        return self._memory_manager

    @property
    def current_session(self):
        return self._sessions[0] if len(self._sessions) > 0 else None

    def status(self, session_id: UUID = None) -> DeviceStatus:
       return self._status
    
    def change_status(self, status: DeviceStatus):
        if status == DeviceStatus.READY and len(self._sessions) <= 0:
            self._status = DeviceStatus.WAITING
        else:
            self._status = status

    
    def set_current_session(self, session_id: UUID):
        '''
            Set the current session to the session_id
            
            Prerequisite: session_id must be in the sessions list
        '''

        if session_id not in self._sessions:
            raise device_exception.DeviceNoSessionException()
        
        self._sessions.remove(session_id)
        self._sessions.insert(0, session_id)




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



    def check_status(*status : list[DeviceStatus]):
        def decorator(func):
            def inner(self, *args, **kwargs):
                if self._status not in status:
                    raise device_exception.DeviceBusyException()
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
    @check_current_session
    @check_status(DeviceStatus.COMPUTING, DeviceStatus.RECORDING)
    def stop_job(self, session_id: UUID):
        '''
            Stop the current job
        '''
        self._current_job.join(timeout=0.001)
        print(f"[DEVICE] Job stopped")
        self._current_job = None
        self.change_status(DeviceStatus.READY)
        return self.status(session_id).name

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

        ## Put session_id as the current session
        self.set_current_session(session_id)


        ## Adding recording and computing here thread based
        self._current_job = RecordLauncher(self, self._records_manager, self._memory_manager, session_id, duration, delay = delay, seed_id = seed_id)
        self._current_job.start()
        

        



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
        '''
            Get the last error and release the device
            Error can be read only by the current session
        '''
        self.change_status(DeviceStatus.READY)
        

        return {"error" : str(self._last_error)}, 200









