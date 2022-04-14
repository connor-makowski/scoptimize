class TypeEnforced:
    def __init__(self, __fn__, *__args__, **__kwargs__):
        self.__doc__=__fn__.__doc__
        self.__name__=__fn__.__name__+"_TypeEnforced"
        self.__annotations__=__fn__.__annotations__
        self.__fn__=__fn__
        self.__args__=__args__
        self.__kwargs__=__kwargs__

    def __call__(self, *args, **kwargs):
        return self.__validate__(*args, **kwargs)

    def __check_type__(self, obj, types, key):
        if not isinstance(types, list):
            types=[types]
        if type(obj) not in types:
            raise Exception(f"Type mismatch for typed function item `{key}`. Expected one of the following `{str(types)}` but got `{type(obj)}` instead.")

    def __validate__(self, *args, **kwargs):
        # Determine assigned variables as they were passed in
        assigned_vars={
            **dict(zip(self.__fn__.__code__.co_varnames[:len(args)], args)),
            **kwargs
        }
        # Create a shallow copy dictionary to preserve annotations at object root
        annotations=dict(self.__annotations__)
        # Validate annotations for all non return types prior to function execution
        for key, value in annotations.items():
            if key in assigned_vars:
                self.__check_type__(assigned_vars.get(key),value, key)
        # Execute the function callable
        return_value=self.__fn__(*args, **kwargs)
        # If a return type was passed, validate the returned object
        if 'return' in annotations:
            self.__check_type__(return_value, annotations['return'], 'return')
        return return_value


    def __repr__(self):
        return f"<TypeEnforced {self.__fn__.__module__}.{self.__fn__.__qualname__} object at {hex(id(self))}>"


@TypeEnforced
def validate(a: str , b: [int, str] =2) -> type(None):
    print(a, b)

validate(1, a='f')
validate(1, 'a')
