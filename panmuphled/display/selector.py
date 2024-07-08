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
            logger.warning(f"Error with selecting window, return code: {rc}")
            return (rc, None)

        sel = stdout.strip("\n")

        return (RC_OK, sel)
    
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