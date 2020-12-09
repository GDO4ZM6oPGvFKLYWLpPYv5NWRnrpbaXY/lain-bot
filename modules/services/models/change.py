from typing import TypeVar

K = TypeVar('K')
#-
O = TypeVar('O')
N = TypeVar('N')

class Change:
    """Generic container for a change

    Attributes:
        kind: Property user can use as a meta tag for the change
        old: Container for representing old value
        new: Container for representing new value
        msg: A message to associate with change
        ignore (bool): Specific flag user can set/get for ignoring change
    """

    __slots__ = ['_old', '_new', '_msg', '_kind', '_ignore']

    def __init__(self, kind: K, old: O, new: N, msg: str) -> None:
        self._old = old
        self._new = new
        self._msg = msg
        self._kind = kind
        self._ignore = False

    @property
    def kind(self) -> K:
        return self._kind

    @property
    def msg(self) -> str:
        return self._msg

    @msg.setter
    def msg(self, msg: str) -> None:
        self._msg = msg

    @property
    def ignore(self) -> bool:
        return self._ignore

    @ignore.setter
    def ignore(self, ignore: bool) -> None:
        self._ignore = ignore

    @property
    def old(self) -> O:
        return self._old

    @property
    def new(self) -> N:
        return self._new
        
    def __repr__(self) -> str:
        return f"<kind={self.kind}, old={self.old}, new={self.new}, ignore={self.ignore}, '{self.msg}'>"

    def __str__(self) -> str:
        return self.msg