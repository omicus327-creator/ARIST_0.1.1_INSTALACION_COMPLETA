from .octoprint import OctoPrint
from .moonraker import Moonraker

def build_printer(config):
    if config.PRINTER_BACKEND=='octoprint': return OctoPrint(config.OCTOPRINT_URL,config.OCTOPRINT_API_KEY)
    if config.PRINTER_BACKEND=='moonraker': return Moonraker(config.MOONRAKER_URL,config.MOONRAKER_API_KEY)
    return None
