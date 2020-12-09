from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable, List, Optional, Union, Any, Dict, Type
    from .change import Change
    from .user import User
    from .profile import Profile
    from .data import Image

from dataclasses import dataclass, field as dcfield

class Field(str):
    """A string with benefits :/

    Attributes:
        default (Any): the default value for the field
        concealed (bool): if field not present in the entry's database representation
        label (str): string representation of field's name

    Methods:
        consume: Produce Change if any difference between supplied values, None if no difference.
    """
    __slots__ = ['consume', 'default', 'concealed']

    @property
    def label(self):
        return str(self)

def field(label: str, default: Any = None, consume_fn: Callable[[Type[ListEntry],Any,Any], Optional[Change]] = lambda *a: None, concealed: bool = False) -> Field:
    """Create a Field with a consume method

    Args:
        label (str): field name
        default (Any): default field value
        consume_fn (Callable): function to produce Change
        concealed (bool, optional): hide from database entry. Defaults to False.

    Returns:
        Field: field
    """
    f = Field(label)
    f.consume = consume_fn
    f.default = default
    f.concealed = concealed
    return f


required_data_fields = ['id', 'attributes']
@dataclass
class Specs:
    DATA_FIELDS: List[Field] = dcfield(default_factory=lambda: [field('id', 0, concealed=True), field('attributes', 0)])
    DYNAMIC_FIELDS: List[Field] = dcfield(default_factory=list)

    def __post_init__(self):
        errs = []
        for f in required_data_fields:
            if f not in self.DATA_FIELDS:
                errs.append(f)

        if errs:
            raise AttributeError(f"Missing required data fields: {', '.join(errs)}")

class ListEntry:
    """Represents an entry in list during sync process. Fields are accessed like 
    a dict, ex: my_entry[field].
    """
    __slots__ = ['fields', '_changes']
    specs = Specs()

    def __init__(self) -> None:
        self._changes = []
        self.fields = {}

    ### dict access functionality. don't override ###
    #|  e.get(key, default) functionality
    def get(self, key: str, default: Any = None) -> Any:
        """Get field by key with optional default if key missing"""
        return self.fields.get(key, default)
    #|  e[key] functionality
    def __getitem__(self, key: str) -> Any:
        return self.fields.get(key)
    #|  e[key] = val functionality
    def __setitem__(self, key: str, val: Any) -> None:
        if not (key in self.specs.DYNAMIC_FIELDS or key in self.specs.DATA_FIELDS):
            raise AttributeError(f"Entry has no '{key}' field")
        self.fields[key] = val

    ### syncer functions. don't override ###
    #|  syncer uses this for knowing what to display
    def changes(self, pruned=True) -> List[Change]:
        """Get changes. Pruning returns list without ignored changes"""
        return [c for c in self._changes if not c.ignore] if pruned else self.changes
    #|  syncer uses this as database entry
    @property
    def dict(self) -> Dict[str, Any]:
        """Dict containing all non-concealed fields"""
        d = {}
        for field in self.specs.DYNAMIC_FIELDS:
            if field.concealed:
                continue
            d[field.label] = self.fields.get(field, field.default)
        for field in self.specs.DATA_FIELDS:
            if field.concealed:
                continue
            d[field.label] = self.fields.get(field, field.default)
        return d
    #|  syncer uses this to produce changes between databse entry and fetched entry
    def consume(self, entry: Union[Type[ListEntry], Dict[str, Any]]) -> None:
        """Generate changes between this entry (new) and provided entry (old)"""
        for field in self.specs.DYNAMIC_FIELDS:
            change = field.consume(self, entry.get(field, field.default), self.fields.get(field, field.default))
            if change:
                self._changes.append(change)

    ### mods for syncer display. override for better display output ###
    #|  syncer calls this for adding images to the embed
    def images(self) -> List[Image]:
        """Images to associate with changes"""
        return []
    #|  syncer calls this before calling changes to allow for modifying changes
    def rationalize_changes(self, user: User = None, latest_profile: Type[Profile] = None) -> None:
        """Post-consume logic to modify/ignore changes. User and fetched profile optioannly provided.

        Args:
            user: The user (from database) associated with the entry. Defaults to None.
            latest_profile: The most recent profile i.e. the fetched one if it was fetched or the one from db user.Defaults to None.
        """
        pass
