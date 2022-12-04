import json
import abc
import traceback


class IRepository(abc.ABCMeta):
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

    @classmethod
    def getInstance(cls) -> IRepository:
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance

    def init(self) -> None:
        with open('switches.json', encoding='utf-8') as switches_file:
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
            print(e.with_traceback())
            raise GetSwitchError()

    def update_state_by_switch_name(self, switch_name, state) -> None:
        if not self.is_initialized():
            raise UnInitializedError()

        try:
            self.switches_state[switch_name]["state"] = state
            with open('switches.json', encoding='utf-8', mode='w') as switches_file:
                json.dump(self.switches_state, switches_file)
        except Exception as e:
            print(traceback.format_exc())
            raise UpdateStateError()