import json
import traceback
import switchbot
from repository import GetSwitchError,UpdateStateError,SwitchNotExistError, IRepository

def is_valid_format(payload: dict)->bool:
    if("switch_name" not in payload):
        print("Switch name is not specified.")
        return False
    if("state" not in payload):
        print("State is not specified")
        return False
    if not isinstance(payload["state"], bool):
        print("State is invalid value.")
        return False
    return True

def exec_switchbot(payload: str, repository: IRepository)->None:
    try:
        received_data = json.loads(payload)
    except json.decoder.JSONDecodeError as e:
        print(e.msg())
        print(traceback.format_exc())
        return


    if is_valid_format(received_data):
        target_switch_name = received_data['switch_name']
        required_state = received_data['state']

        try:
            current_state = repository.get_switch_record_by_switch_name(target_switch_name)
        except SwitchNotExistError:
            print("Switch {} is not registered.".format(target_switch_name))
            return
        except GetSwitchError:
            print("Read state failed.")
            return


        if current_state["state"] != required_state:
            if switchbot.execute(mac=current_state["mac"], dev_type="Bot", cmd="Press"):
                try:
                    repository.update_state_by_switch_name(target_switch_name, required_state)
                except UpdateStateError as e:
                    print("Update state failed.")
                    return
        else:
            print("Already switch is {}".format("ON" if required_state else "OFF"))
