from dataclasses import dataclass

@dataclass
class DCSCommand:

    PITCH = 2001
    ROLL = 2002
    RUBBER = 2003
    THRUST = 2004
    RESET = 327
    RESTART_MISSION = 1641
    EJECT = 83
    
    
    
    UPSTART = 193
    UPSTOP = 194
    DOWNSTART = 195
    DOWNSTOP = 196
    LEFTSTART = 197
    LEFTSTOP = 198
    RIGHTSTART = 199
    RIGHTSTOP = 200

def parse_command(command_dict):
    """
        Parse input action command dictionary to lua format.

        An example for input action format:
        {
            2001: 0.0,
            2002: 0.0,
            327: Ture,
            ......
        }
    """
    
    action_string_list = []
    for k, v in command_dict.items():
        if isinstance(v, bool):
            v = 'true' if v else 'false'
        action_string_list.append( f"[{k}]= {v}" )

    action_string = ', '.join(action_string_list)
    return '{' + action_string + '}'
    # return action_string
    # command = f"{{['pitch']= {pitch}, ['roll']= {roll}, ['rudder']= {rubber}, ['thrust']= {thrust}}}"
