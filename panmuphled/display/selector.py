import logging

from panmuphled.display.common import run_command

logger = logging.getLogger(__name__)

RC_OK = 0
RC_BAD = 1

class Selector:
    @staticmethod
    def select_from_list(lst):
        stdin_str = "\n".join(lst)
        rc, stdout = run_command(["/usr/bin/rofi", "-dmenu"], input=stdin_str)

        if rc != RC_OK:
            logger.warning(f"Error with selecting from list, return code: {rc}")
            return (rc, None)

        sel = stdout.strip("\n")

        return (RC_OK, sel)
    
    @staticmethod
    def select_workspace(ctlr):
        workspaces = ctlr.get_workspaces()
        ws_table = {}

        for ws in workspaces:
            ws_table[ws.name] = ws

        rc, sel_ws = Selector.select_from_list(list(ws_table.keys()))

        if rc != RC_OK:
            logger.warning(f"Selection failed with RC: {rc}")
            return {"rc": RC_BAD}

        if sel_ws not in ws_table:
            logger.warning(f"Selected workspace not found: '{sel_ws}'")
            return {"rc": RC_BAD}
        
        return ws_table[sel_ws]

    @staticmethod
    def select_window(ctlr, ws_name=None, all_win=False):
        windows = ctlr.get_windows(ws_name=ws_name, all_win=all_win)
        wn_table = {}

        for wn in windows:
            wn_table[wn.name] = wn

        rc, sel_wn = Selector.select_from_list(list(wn_table.keys()))

        if rc != RC_OK:
            logger.warning(f"Selection failed with RC: {rc}")
            return {"rc": RC_BAD}

        if sel_wn not in wn_table:
            logger.warning(f"Selected window not found: '{sel_ws}'")
            return {"rc": RC_BAD}
        
        return rc, wn_table[sel_wn]
    
    @staticmethod
    def select_application():
        rc, stdout = run_command(["/usr/bin/rofi", "-show", "drun", "-run-command", '"echo {cmd}"'])

        if rc != RC_OK:
            logger.warning(f"Error with selecting application, return code: {rc}")
            return (rc, None)

        sel = stdout.strip("\n")

        return (RC_OK, sel)

    @staticmethod
    def enter_text():
        # This hack has three parts:
        #  -kb-accept-custom is set to 'Return' key so that it accepts whatever string the user
        #  has written
        #  -kb-accept-entry  is set to 'Ctrl+Return' so that the 'Return' key is free for use
        #  -l overrides the number of lines to 0, which makes the text box look like just an input
        #   field and basically nothing else
        rc, stdout = run_command(["/usr/bin/rofi", 
            "-dmenu",
            "-kb-accept-custom", "'Return'", 
            "-kb-accept-entry", "'Ctrl+Return'",
            "-l", "0"
            ], input="")