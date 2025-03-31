from pipewire_python.controller import Controller
from utils import HiddenPrints


class PWController(Controller):
    def __init__(self, verbose=False):
        super().__init__(verbose)

    def getTargets(self, verbose=False):
        targets = None

        with HiddenPrints():
            targets = self.get_list_interfaces(
                type_interfaces='Node'
            )

        if verbose:
            return targets

        res = dict()
        for serial in targets:
            name = targets[serial]["properties"]["node.name"]
            res[serial] = name

        return res
