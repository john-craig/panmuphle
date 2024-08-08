import logging

logger = logging.getLogger(__name__)

RC_OK = 0
RC_BAD = 1

class Parser
    @staticmethod
    parse_index(msg):
        rc = RC_OK

        if "index" not in msg:
            return [rc, None]
        else:
            if type(msg["index"]) != int:
                logger.warning(f"Found index with invalid type while parsing message")
                return {"rc": RC_BAD}
            else:
                return [rc, msg["index"]]

    @staticmethod
    parse_name(msg):
        rc = RC_OK

        if "name" not in msg:
            return [rc, None]
        else:
            if type(msg["name"]) != str:
                logger.warning(f"Found name with invalid type while parsing message")
                return {"rc": RC_BAD}
            else:
                return [rc, msg["name"]]


    @staticmethod
    parse_exec(msg):
        rc = RC_OK

        if "exec" not in msg:
            return [rc, None]
        else:
            if type(msg["exec"]) != str:
                logger.warning(f"Found exec with invalid type while parsing message")
                return {"rc": RC_BAD}
            else:
                return [rc, msg["exec"]]

    @staticmethod
    parse_pid(msg):
        rc = RC_OK

        if "pid" not in msg:
            return [rc, None]
        else:
            if type(msg["pid"]) != int:
                logger.warning(f"Found pid with invalid type while parsing message")
                return {"rc": RC_BAD}
            else:
                return [rc, msg["pid"]]

    @staticmethod
    parse_message(msg, required=[], optional=[]):
        # This is a one-stop shop for everything we need to do vis-a-vis
        # parsing and validating the contents of a message
        rc = RC_OK

        resp_req = {}
        resp_opt = {}

        for key in required:
            resp_req[key] = None
        
        for key in optional:
            resp_opt[key] = None

        if "workspace" in msg:
            ws_msg = msg["workspace"]

            # Handle index
            rc, ws_index = Parser.parse_index(ws_msg)

            if rc != RC_OK:
                return [rc] + ([None] * len(required)) + ([None] * len(optional))
            
            if "ws_index" in resp_req:
                resp_req["ws_index"] = ws_index
        
            if "ws_index" in resp_opt:
                resp_opt["ws_index"] = ws_index

            # Handle name
            rc, ws_name = Parser.parse_name(ws_msg)

            if rc != RC_OK:
                return [rc] + ([None] * len(required)) + ([None] * len(optional))
            
            if "ws_name" in resp_req:
                resp_req["ws_name"] = ws_name
        
            if "ws_name" in resp_opt:
                resp_opt["ws_name"] = ws_name
        if "window" in msg:
            wn_msg = msg["window"]

            # Handle index
            rc, wn_index = Parser.parse_index(wn_msg)

            if rc != RC_OK:
                return [rc] + ([None] * len(required)) + ([None] * len(optional))
            
            if "wn_index" in resp_req:
                resp_req["wn_index"] = wn_index
        
            if "wn_index" in resp_opt:
                resp_opt["wn_index"] = wn_index

            # Handle name
            rc, wn_name = Parser.parse_name(wn_msg)

            if rc != RC_OK:
                return [rc] + ([None] * len(required)) + ([None] * len(optional))
            
            if "wn_name" in resp_req:
                resp_req["wn_name"] = wn_name
        
            if "wn_name" in resp_opt:
                resp_opt["wn_name"] = wn_name
        
        if "application" in msg:
            app_msg = msg["application"]

            # Handle index
            rc, app_index = Parser.parse_index(app_msg)

            if rc != RC_OK:
                return [rc] + ([None] * len(required)) + ([None] * len(optional))
            
            if "app_index" in resp_req:
                resp_req["app_index"] = app_index
        
            if "app_index" in resp_opt:
                resp_opt["app_index"] = app_index

            # Handle name
            rc, app_name = Parser.parse_name(app_msg)

            if rc != RC_OK:
                return [rc] + ([None] * len(required)) + ([None] * len(optional))
            
            if "app_name" in resp_req:
                resp_req["app_name"] = app_name
        
            if "app_name" in resp_opt:
                resp_opt["app_name"] = app_name
        
            # Handle pid
            rc, app_pid = Parser.parse_pid(app_msg)

            if rc != RC_OK:
                return [rc] + ([None] * len(required)) + ([None] * len(optional))
            
            if "app_pid" in resp_req:
                resp_req["app_pid"] = app_pid
        
            if "app_pid" in resp_opt:
                resp_opt["app_pid"] = app_pid
            
            # Handle exec
            rc, app_exec = Parser.parse_exec(app_msg)

            if rc != RC_OK:
                return [rc] + ([None] * len(required)) + ([None] * len(optional))
            
            if "app_exec" in resp_req:
                resp_req["app_exec"] = app_exec
        
            if "app_exec" in resp_opt:
                resp_opt["app_exec"] = app_exec


        # Make sure all the required keys were found
        for key in resp_req:
            if resp_req[key] == None:
                return [RC_BAD] + ([None] * len(required)) + ([None] * len(optional))
        
        resp_all = []

        for key in resp_req:
            resp_all.append(resp_req[key])
        
        for key in resp_opt:
            resp_all.append(resp_opt[key])
        
        return [rc] + resp_all