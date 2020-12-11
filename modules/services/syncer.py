from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, Type, List
    from .models.query import Query
    from .models.data import FetchData
    from discord.ext.commands import bot
    from modules.services.models.entry import ListEntry
    from io import BytesIO
    
from . import Service
import asyncio, discord, datetime
from .models.user import User, UserStatus
from .models.data import ResultStatus, Image
from modules.core.resources import Resources
import time

class Syncer:

    def __init__(self, bot: bot, service: str, query: Type[Query], sleep_time: float = 30) -> None:
        print(f"{service} service registered!")
        self.bot = bot
        self.service = service
        self.query = query
        self.sleep_time = sleep_time

    async def loop(self) -> None:
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            cursor = Resources.user2_col.find({'status': UserStatus.ACTIVE, 'service': self.service})
            try:
                users = await cursor.to_list(length=self.query.MAX_USERS_PER_QUERY)
            except:
                users = []
                print(f'initial batch fail for {self.service}')

            while users:
                users = [User(**user) for user in users] # format document to User
                names = [u.profile.name for u in users]
                
                # print(f"{self.service}::{names}")
                fetch_start = time.time()
                fetched_data = await self.query.fetch(users) # query new data for users

                # handle each user
                for user in users:
                    user_data = fetched_data.get(user._id)

                    if not user_data: # query didn't populate this user
                        print(f"no user data for {names}")
                        continue # skip
                    
                    # generate changes and get all entries from each list that have (pruned) changes
                    comprehensions = await self.bot.loop.run_in_executor(
                        None, 
                        self._comprehend,
                        user,
                        user_data
                    )

                    # send changes
                    await self._display(user, comprehensions)

                    # # update db
                    if user_data.profile.status == ResultStatus.OK:
                        user.profile = user_data.profile.data
                    for lst in user_data.lists:
                        if user_data.lists[lst].status == ResultStatus.OK:
                            k = {}
                            for entry in user_data.lists[lst].data:
                                k[str(entry['id'])] = entry.dict
                            user.lists[lst] = k
                    await Resources.user2_col.update_one(
                        {'discord_id': user.discord_id, 'service': user.service},
                        {'$set': user.dict}
                    )
            
                users_end = time.time()
                # ready new batch from db
                try:
                    users = await cursor.to_list(length=self.query.MAX_USERS_PER_QUERY)
                except:
                    print(f'new batch fail for {self.service}')
                    users = []
                finally:
                    sleep_corrected = max(0, self.sleep_time - (users_end-fetch_start))
                    await asyncio.sleep(sleep_corrected)
        
            # done with all the batches, start new round of batches
            await cursor.close()

    @staticmethod
    def _comprehend(user: User, data: FetchData) -> Dict[str, List[ListEntry]]:
        comprehensions = {}
        for lst in data.lists:
            if data.lists[lst].status == ResultStatus.OK:
                comprehensions[lst] = []
                for entry in data.lists[lst].data:
                    entry.consume(user.lists.get(lst, {}).get(str(entry['id']), {}))
                    if data.profile.status == ResultStatus.OK:
                        entry.rationalize_changes(user, data.profile.data)
                    else:
                        entry.rationalize_changes(user, user.profile)
                    if entry.changes(pruned=True):
                        comprehensions[lst].append(entry)
        return comprehensions  

    async def _display(self, user: User, comprehensions: Dict[str, List[ListEntry]]) -> None:
        # nothin
        if not comprehensions:
            return

        # myanimelist doesn't populate list data* when finding user to save on 
        # time and APi rate limits, so ignore displaying the first sync since 
        # it'll see everything as a change and have a massive output.
        # *it actually populates a single empty anime entry to signify having 
        # never been synced before
        if user.service == Service.MYANIMELIST:
            if 'None' in user.lists['anime']:
                return
            
        # only use lists with changes
        tmp = {}
        for lst in comprehensions:
            if comprehensions[lst]:
                tmp[lst] = comprehensions[lst]
        comprehensions = tmp

        # no list had changes
        if not comprehensions:
            return
        
        combined_images = {} # rudimentary caching for generated images
        try:
            disaply_guild_ids = []
            for guild in self.bot.guilds:
                # check if this guild contains that user
                try: member = await guild.fetch_member(int(user.discord_id))
                except: member = None
                if member: 
                    disaply_guild_ids.append(str(guild.id))
            if not disaply_guild_ids:
                return
            
            # display for each of those guilds based on its settings
            async for guild in Resources.guild2_col.find({'guild_id': {'$in': disaply_guild_ids}}):
                # go through all the channels it displays updates for
                for ch in guild['settings']['updates']:
                    channel = self.bot.get_channel(int(ch))
                    lists = guild['settings']['updates'][ch]
                    if not (channel and lists): # make sure that channel is valid (exists in guild and has >0 display lists enabled)
                        continue
                    # genrate and send embed/files
                    msgs = {}
                    imgs = []
                    for lst in lists:
                        m = []
                        changed_entries = comprehensions.get(lst, [])
                        for entry in changed_entries:
                            if entry['attributes'] & guild['settings']['entry_ignore_attributes']:
                            # ignore if entry has any atributes guild want to ignore
                                continue
                            for change in entry.changes(pruned=True):
                                m.append(change.msg)
                            if entry['attributes'] & guild['settings']['image_ignore_attributes']: 
                            # ignore images if entry has attributes guild want to ignore images for
                                continue
                            imgs.extend(entry.images())
                        if m:
                            msgs[lst] = m
                    await self._embed(channel, user, msgs, imgs, combined_images)
        except Exception as e:
            # TODO: log display didn't work
            print(e.message)
        finally:
            # free up resources used
            # gc will eventually close 'em but might as well be cleaner
            for s in combined_images:
                combined_images[s].close()

    async def _embed(self, channel, user: User, msgs: Dict[str, List[str]], imgs: List[Image], img_stash: Dict[int, BytesIO]) -> None:
        if not msgs:
            return

        nick = ''
        for member in channel.members:
            if str(member.id) == user.discord_id:
                nick = member.nick if member.nick else member.name
                break
        try:
            name = f"{user.profile.name} ({nick})"
        except:
            if nick:
                name = nick
            else:
                name = '*unknown*'

        embed = discord.Embed(
            title = name,
            url = Service(user.service).link(user.service_id)
        )
        embed.set_footer(text='This message was generated ' + Resources.timezone.localize(datetime.datetime.now()).strftime('%b %d, %Y at %I:%M %p (CT)'))
        try: embed.set_thumbnail(url=user.profile.avatar)
        except: pass

        for lst in msgs:
            embed.add_field(name=f"Updated their {lst} list", value=self._limit_msgs(msgs[lst]), inline=False)

        if len(imgs) == 1:
            embed.set_image(url=imgs[0].wide)
            return await channel.send(embed=embed)
        elif len(imgs) > 1:
            imgs = frozenset([i.narrow for i in imgs][:6])
            fn = f"{hash(imgs)}.jpg"
            fp = img_stash.get(fn)
            if not fp:
                fp = await Resources.img_gen.combineUrl(Resources.syncer_session, self.bot.loop, imgs)
                img_stash[fn] = fp
            else:
                fp.seek(0)
            embed.set_image(url=f"attachment://{fn}")
            f = discord.File(fp, filename=fn)
            return await channel.send(file=f, embed=embed)
        else:
            return await channel.send(embed=embed)

    def _limit_msgs(self, msgs, limit=6):
        num_changes = len(msgs)

        change_msg = ''
        if num_changes > limit:
            msgs = msgs[0:limit]
            change_msg = '\n'.join([f"• {msg}" for msg in msgs])
            change_msg = f"{change_msg}\n• and {num_changes-limit} other changes!"
        else:
            change_msg = '\n'.join([f"• {msg}" for msg in msgs])
        
        if len(change_msg) > 1024:
            try: change_msg = self._reduce(msgs)
            except: pass

        return change_msg

    def _reduce(self, changes):
        cnt = len(changes)
        extra = '• and {cnt} other changes!'
        change_msgs = ''
        for change in changes:
            if len(change_msgs) + len(change.msg) + len(extra.format(cnt=cnt)) + 3 > 1024: # discord limits filed to 1024 characters
                break
            cnt -= 1
            change_msgs = f"{change_msgs}• {change.msg}\n"

        change_msgs = f"{change_msgs}{extra.format(cnt=cnt)}"
        return change_msgs
