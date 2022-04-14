
class TypeEnforced:
    def __init__(self, __fn__, *__args__, **__kwargs__):
        self.__doc__=__fn__.__doc__
        self.__name__=__fn__.__name__+"_TypeEnforced"
        self.__annotations__=__fn__.__annotations__
        self.__fn__=__fn__
        self.__args__=__args__
        self.__kwargs__=__kwargs__

    def __call__(self, *args, **kwargs):
        # print(args, kwargs)
        # print(self.__annotations__)
        print(dir(self.__fn__))
        print(self.__fn__.__kwdefaults__)
        return self.__fn__(*args, **kwargs)

    def __repr__(self):
        return f"<TypeEnforced {self.__fn__.__module__}.{self.__fn__.__qualname__} object at {hex(id(self))}>"


@TypeEnforced
def validate(a, b: [int, str]) -> None:
    # if type(a) not in [validate.__annotations__['a']]:
    #     print('Invalid')
    pass

validate('f', b=1)
# validate(a=1, b='a')
