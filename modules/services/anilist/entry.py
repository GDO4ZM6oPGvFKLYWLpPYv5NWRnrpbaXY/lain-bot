from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.user import User
    from typing import Optional, Union, List
    from .profile import WeebProfile

from ..models.entry import ListEntry, field, Specs
from ..models.data import Image
from ..models.change import Change
from .enums import Status, ScoreFormat, ChangeKind

def status_consumer(self: AnimeEntry, old: str, new: str) -> Optional[Change]:
    if old == new:
        return None
    msg = f"{self['title']} added to {new} list"
    if new in [Status.COMPLETED, Status.DROPPED, Status.PAUSED]:
        msg = f"{new} {self['title']}"
    return Change(ChangeKind.STATUS, old, new, msg)

def score_consumer(self: AnimeEntry, old: Union[float, int], new: Union[float, int]) -> Optional[Change]:
    if old == new:
        return None
    return Change(ChangeKind.SCORE, old, new, f"score of {self['title']} changed: {old} ➔ {new}")

def episode_consumer(self: AnimeEntry, old: int, new: int) -> Optional[Change]:
    if old >= new:
        return None
    msg = f"watched episode {new} of {self['title']}"
    if new - old > 1:
        msg = f"watched episodes {old+1}-{new} of {self['title']}"
    return Change(ChangeKind.PROGRESS, old, new, msg)

def chapter_consumer(self: AnimeEntry, old: int, new: int) -> Optional[Change]:
    if old >= new:
        return None
    msg = f"read chapter {new} of {self['title']}"
    if new - old > 1:
        msg = f"read chapters {old+1}-{new} of {self['title']}"
    return Change(ChangeKind.PROGRESS, old, new, msg)

def volume_consumer(self: AnimeEntry, old: int, new: int) -> Optional[Change]:
    if old >= new:
        return None
    msg = f"read volume {new} of {self['title']}"
    if new - old > 1:
        msg = f"read volumes {old+1}-{new} of {self['title']}"
    return Change(ChangeKind.PROGRESS, old, new, msg)

def rationalizer(self, user: User, latest_profile: WeebProfile = None) -> None:
    if not self.changes():
        return

    old_score_format = ScoreFormat(user.profile.score_format)
    new_score_format = ScoreFormat(latest_profile.score_format) if latest_profile else old_score_format

    status_change = None
    score_change = None
    progress_changes = []
    for c in self.changes():
        if c.kind == ChangeKind.STATUS:
            status_change = c
        elif c.kind == ChangeKind.SCORE:
            score_change = c
        elif c.kind == ChangeKind.PROGRESS:
            progress_changes.append(c)

    def ignore_progress_changes():
        for pc in progress_changes:
            pc.ignore = True
    
    # handle case of adding re to read/watch for repeating media
    if progress_changes and self['status'] == Status.REPEATING:
        for pc in progress_changes:
            pc.msg = f"re{pc.msg}"

    # rationalize various special cases of status changes
    if status_change:
        if status_change.new in [Status.CURRENT, Status.REPEATING]:
            # have progress changes overrule adding to current/repeating list
            if progress_changes:
                status_change.ignore = True
        if status_change.new in [Status.DROPPED, Status.PAUSED]:
            # have dropped/paused status overrule any progress changes
            ignore_progress_changes()
            if self.has_progress:
                status_change.msg = f"{status_change.msg} on {self.progress}"
        if status_change.new == Status.COMPLETED:
            # have completed status overrule any progress or score changes
            if score_change: score_change.ignore = True
            ignore_progress_changes()
            if self['score']:
                # include score of completed media if available
                status_change.msg = f"{status_change.msg} with a score of {new_score_format.formatted_score(self['score'])}"

    # special case where user changes score format and all their scores adjust to it
    if new_score_format != old_score_format:
        if score_change: score_change.ignore = True

    # use dynamic score formatting depending on user's score format
    if score_change:
        old = old_score_format.formatted_score(score_change.old)
        new = new_score_format.formatted_score(score_change.new)
        if score_change.old == 0:
            score_change.msg = f"score of {self['title']} set to {new}"
        else:
            score_change.msg = f"score of {self['title']} changed: {old} ➔ {new}"

def img(self) -> List[Image]:
    if self['banner'] and self['cover']:
        return [Image(narrow=self['cover'], wide=self['banner'])]
    elif self['banner']:
        return [Image(narrow=self['banner'], wide=self['banner'])]
    elif self['cover']:
        return [Image(narrow=self['cover'], wide=self['cover'])]
    else:
        return []

class AnimeEntry(ListEntry):
    specs = Specs(
        DATA_FIELDS=[
            field('id', 0, concealed=True),
            field('attributes', 0, concealed=True),
            field('banner', '', concealed=True),
            field('cover', '', concealed=True),
            field('title', ''),
            field('episodes', 0)
        ],
        DYNAMIC_FIELDS=[
            field('score', 0, score_consumer),
            field('episode_progress', 0, episode_consumer),
            field('status', Status.UNKNOWN, status_consumer)
        ]
    )

    @property
    def progress(self) -> str:
        return f"episode {self['episode_progress']}"

    @property
    def has_progress(self) -> bool:
        return bool(self['episode_progress'])

    rationalize_changes = rationalizer

    images = img

class MangaEntry(ListEntry):
    specs = Specs(
        DATA_FIELDS=[
            field('id', 0, concealed=True),
            field('attributes', 0, concealed=True),
            field('banner', '', concealed=True),
            field('cover', '', concealed=True),
            field('title', ''),
            field('chapters', 0),
            field('volumes', 0)
        ],
        DYNAMIC_FIELDS=[
            field('score', 0, score_consumer),
            field('chapter_progress', 0, chapter_consumer),
            field('volume_progress', 0, volume_consumer),
            field('status', Status.UNKNOWN, status_consumer)
        ]
    )

    @property
    def progress(self) -> str:
        if self['volume_progress']:
            return f"volume {self['volume_progress']}"
        else:
            return f"chapter {self['chapter_progress']}"

    @property
    def has_progress(self) -> bool:
        return bool(self['volume_progress']) or bool(self['chapter_progress'])

    rationalize_changes = rationalizer

    images = img
