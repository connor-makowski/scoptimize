from pamda import utils

Large_M = 10**16


class TypeChecker(utils.error):
    def check_type(self, fn, obj, accepted_objects):
        if type(obj) not in accepted_objects:
            self.exception(
                f"{fn} only accepts {str(accepted_objects)} but you passed an object of type: {type(obj)}"
            )
