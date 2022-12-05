import json
import abc
import traceback
from threading import Lock


class IRepository(abc.ABC):
    @abc.abstractmethod
    def init(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_switch_record_by_switch_name(self, switch_name: str) -> dict:
        raise NotImplementedError()

    @abc.abstractmethod
    def update_state_by_switch_name(self, switch_name: str, state: bool) -> bool:
        raise NotImplementedError()

class SwitchNotExistError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class GetSwitchError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class UpdateStateError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class UnInitializedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class JsonFileRepository(IRepository):
    switches_state = {}
    initialize_flag = False
    db_file = "db/switches.json"
    _lock = Lock()


    def __new__(cls):
        raise NotImplementedError('Cannnot initialize via constructor, must use get_instance')

    @classmethod
    def get_instance(cls) -> IRepository:
        if not hasattr(cls, '_instance'):
            with cls._lock:
                cls._instance = super().__new__(cls)
        return cls._instance

    def init(self) -> None:
        with self._lock:
            if not self.initialize_flag:
                with open(self.db_file, encoding='utf-8') as switches_file:
                    self.switches_state = json.load(switches_file)
                self.initialize_flag = True

    def is_initialized(self) -> bool:
        return self.initialize_flag

    def get_switch_record_by_switch_name(self,switch_name) -> dict:
        if not self.is_initialized():
            raise UnInitializedError()
        try:
            return self.switches_state[switch_name]
        except KeyError as e:
            print(traceback.format_exc())
            raise SwitchNotExistError()

        except Exception as e:
            print(traceback.format_exc())
            raise GetSwitchError()

    def update_state_by_switch_name(self, switch_name, state) -> None:
        if not self.is_initialized():
            raise UnInitializedError()

        try:
            with self._lock:
                self.switches_state[switch_name]["state"] = state
                with open(self.db_file, encoding='utf-8', mode='w') as switches_file:
                    json.dump(self.switches_state, switches_file)
        except Exception as e:
            print(traceback.format_exc())
            raise UpdateStateError()