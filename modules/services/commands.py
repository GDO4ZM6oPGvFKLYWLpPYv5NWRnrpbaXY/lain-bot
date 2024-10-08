from modules.services.models.data import EntryAttributes, ResultStatus
import discord, asyncio
from discord.ext import commands
from discord import app_commands
from modules.core.resources import Resources
from modules.services import Service, Services
from modules.services.models.user import UserStatus, User

from typing import Literal

class ServiceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def services(self, ctx, *args):
        '''For list update stuff. Use '>services' for details'''
        # await ctx.trigger_typing()
        if not args:
            embed = discord.Embed(
                title='Service information',
                description='info pertaining to lists the bot can track updates for and the service(s) available for tracking said list(s)'
            )
            all = Service.all()
            active = Service.active()
            inactive = list(set(all) - set(active))

            active = list(map(lambda service: f"**{service}**: {', '.join(Service(service).list_names)}", active))
            inactive = list(map(lambda service: f"**{service}**: {', '.join(Service(service).list_names)}", inactive))

            if active:
                embed.add_field(name='__Available__', value='\n'.join(active), inline=True)
            else:
                embed.add_field(name='__Available__', value='*None*', inline=True)

            if inactive:
                embed.add_field(name='__Unavailable (WIP/Brokey)__', value='\n'.join(inactive), inline=True)

            guild = await Resources.guild_col.find_one({'guild_id': str(ctx.guild.id)})
            
            update_channels = guild['settings']['updates'] if guild else guild

            if update_channels:
                settings = list(map(lambda ch_id: f"<#{ch_id}>: {', '.join(update_channels[ch_id])}", update_channels))
                embed.add_field(name='__Active in this guild__', value='\n'.join(settings), inline=True)
            else:
                embed.add_field(name='__Active in this guild__', value='*None*', inline=True)

            user_services = Resources.user_col.find({'discord_id': str(ctx.author.id), 'status': { '$not': { '$eq': UserStatus.INACTIVE } }}, {'service': 1, 'status': 1})
            user_services = await user_services.to_list(length=None)

            if user_services:
                user_services = list(map(lambda doc: f"{doc['service']}{' (updates hidden)' if doc['status'] == UserStatus.CACHEONLY else ''}", user_services))
                embed.add_field(name='__Your services__', value='\n'.join(user_services), inline=True)
            else:
                embed.add_field(name='__Your services__', value='*None*', inline=True)

            if guild:
                ignore_flags = EntryAttributes(guild['settings']['entry_ignore_attributes'])
                ignore_img_flags = EntryAttributes(guild['settings']['image_ignore_attributes'])
                msgs = []
                for flag in EntryAttributes:
                    in_ignore = flag in ignore_flags
                    in_ignore_img = flag in ignore_img_flags
                    if in_ignore:
                        msgs.append(f"{flag.name}: *ignoring*")
                    elif in_ignore_img:
                        msgs.append(f"{flag.name}: *ignoring images*")
                    else:
                        msgs.append(f"{flag.name}: *displaying*")
                embed.add_field(name='__Display Filters__', value='\n'.join(msgs), inline=True)

            embed.add_field(
                name='__Usage__', 
                value=(
                    '`>services enable/disable <list>` \nshow list updates in channel command was typed. (requires admin role)\n\n'
                    '`>services filter` \nbring up panel to ignore updates that have certain attributes (admin)\n\n'
                    '`>services filterImages` \nbring up panel to ignore just images in updates that have certain attributes (admin)\n'
                    '*using filter will naturally override filterImage if setting filter to ignore*\n\n'
                ), 
                inline=False)

            await ctx.send(embed=embed)
        else:
            await self._services_mod(ctx, *args)

    @app_commands.command(name="link")
    @app_commands.describe(username='your username on the anime list site')
    async def slash_link(self, interaction, service: Services, username: str):
        """register your anime list with lain"""
        return await self._set_user(interaction, service.value, username)

    @app_commands.command(name="unlink")
    async def slash_unlink(self, interaction, service: Services):
        """remove your anime list from lain"""
        return await self._rem_user(interaction, service.value)

    async def _services_mod(self, ctx, *args):
        if args[0] in ['enable', 'disable']:
            if not ctx.author.guild_permissions.administrator:
                return await ctx.send(f"Only an administrator can modify list updates")

            if not len(args) > 1:
                return await ctx.send(f"Please provide a list to {args[0]}")
            
            lists = []
            for service in Service.all():
                lists.extend(service.list_names)

            if args[1] not in lists:
                return await ctx.send(f"That list does not exist")

            if args[0] == 'enable':
                return await self._enable_list(ctx, args[1])
            else:
                return await self._disable_list(ctx, args[1])

        elif args[0] == 'filter':
            if not ctx.author.guild_permissions.administrator:
                return await ctx.send(f"Only an administrator can modify filters")
            return await self._filter(ctx)

        elif args[0] == 'filterImages':
            if not ctx.author.guild_permissions.administrator:
                return await ctx.send(f"Only an administrator can modify filters")
            return await self._filter(ctx, onlyImages=True)

        elif args[0] == 'hideupdates':
            return await self._hide_updates(ctx, True)
        
        elif args[0] == 'showupdates':
            return await self._hide_updates(ctx, False)

        return await ctx.send('I don\'t recognize that service or command')

    async def _filter(self, ctx, onlyImages=False):
        # await ctx.trigger_typing()
        selectors = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣'] # needs expanding if possible options exceed 9
        selections = {}

        embed = discord.Embed(
            title=f"Set {'image ' if onlyImages else ''}filters",
            description='React to the corresponding emoji to apply the ignore filter, the others will the displaying. Hit ✅ to confirm or ❌ to cancel.'
        )

        current = await Resources.guild_col.find_one({'guild_id': str(ctx.guild.id)})
        ignore_flags = EntryAttributes(current['settings']['entry_ignore_attributes']) if current else EntryAttributes.adult
        ignore_img_flags = EntryAttributes(current['settings']['image_ignore_attributes']) if current else EntryAttributes.adult
        msgs = []
        for flag in EntryAttributes:
            in_ignore = flag in ignore_flags
            in_ignore_img = flag in ignore_img_flags
            selection = selectors.pop(0)
            if in_ignore:
                msgs.append(f"{selection} {flag.name}: *ignoring via main filter*")
            elif in_ignore_img:
                msgs.append(f"{selection} {flag.name}: *ignoring images*")
            else:
                msgs.append(f"{selection} {flag.name}: *displaying*")
            selections[selection] = flag
        embed.add_field(name=f"__{'Image ' if onlyImages else ''}Filters (and current setting)__", value='\n'.join(msgs), inline=True)
        msg = await ctx.send(embed=embed)
        for rxn in selections:
            await msg.add_reaction(rxn)
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')

        def check(reaction, user):
            return user == ctx.message.author and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

        try:
            reaction, author = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send('timed out. settings NOT changed')
        else:
            if str(reaction.emoji) == '✅':
                # await ctx.trigger_typing()
                selected = 0
                msg = await ctx.channel.fetch_message(msg.id)
                for rxn in msg.reactions:
                    if rxn.count > 1:
                        if str(rxn) not in selections:
                            continue
                    usrs = await rxn.users().flatten()
                    if ctx.message.author in usrs:
                        selected = selected | selections[str(rxn)]
                new_settings = EntryAttributes(selected).value
                path = 'settings.entry_ignore_attributes'
                if onlyImages:
                    path = 'settings.image_ignore_attributes'
                if not current:
                    await Resources.guild_col.update_one(
                        {'guild_id': str(ctx.guild.id)}, 
                        {
                            '$set': {
                                'name': ctx.guild.name,
                                'settings': {
                                    'updates': {},
                                    'entry_ignore_attributes': new_settings if not onlyImages else EntryAttributes.adult,
                                    'image_ignore_attributes': new_settings if onlyImages else EntryAttributes.adult
                                }
                            }
                        },
                        upsert=True
                    )
                else:
                    await Resources.guild_col.update_one({'guild_id': str(ctx.guild.id)}, {'$set': {path: new_settings}})
                await ctx.send('setting applied successfully!')
            else:
                await ctx.send('canceled. no filters changed')

    async def _set_user(self, interaction, service, name):
        await interaction.response.defer()
        user = Service(service).Query()
        user = await user.find(name)

        if user.status != ResultStatus.OK:
            if user.status == ResultStatus.NOTFOUND:
                try: await interaction.followup.send(content=f"Could not find any user on {service} with username '{name}'")
                finally: return
            else:
                try: await interaction.followup.send(content=f"Error! {user.data}")
                finally: return
        
        embed = discord.Embed(
            title = name,
            url = user.link,
        )
        embed.set_thumbnail(url=user.image)

        msg = await interaction.followup.send(content='Is this you?', embed=embed, wait=True)

        def check(reaction, user):
            return user == interaction.user and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

        await msg.add_reaction('✅')
        await msg.add_reaction('❌')

        try:
            reaction, author = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            return await interaction.followup.send(content='Timed out. Details NOT updated')
        else:
            if str(reaction.emoji) == '✅':
                new_user = User(
                    discord_id=str(interaction.user.id),
                    service=service,
                    service_id=user.id,
                    status=UserStatus.ACTIVE
                )
                if user.data:
                    if user.data.profile.status == ResultStatus.OK:
                        new_user.profile = user.data.profile.data

                    for lst in user.data.lists:
                        if user.data.lists[lst].status == ResultStatus.OK:
                            k = {}
                            for entry in user.data.lists[lst].data:
                                k[str(entry['id'])] = entry.dict
                            new_user.lists[lst] = k

                await Resources.user_col.update_one(
                    {
                        'discord_id': new_user.discord_id,
                        'service': new_user.service
                    }, 
                    {'$set': new_user.dict},
                    upsert=True
                )
                await interaction.followup.send(content='Your details have been updated!')
            else:
                await interaction.followup.send(content='Your details have NOT been updated!')

    async def _rem_user(self, interaction, service):
        user_id = str(interaction.user.id)
        res = await Resources.user_col.delete_one(
            {
                'discord_id': user_id,
                'service': service
            }
        )
        if res.deleted_count:
            Resources.removal_buffers[service].add(user_id)
            await interaction.response.send_message(f"You have been removed form the {service} service!")
        else:
            await interaction.response.send_message('Failure. User not removed or not found.')

    async def _enable_list(self, ctx, lst):
        await Resources.guild_col.update_one(
            {'guild_id': str(ctx.guild.id)}, 
            {
                '$set': {'name': ctx.guild.name},
                '$setOnInsert': {'settings.entry_ignore_attributes': EntryAttributes.adult, 'settings.image_ignore_attributes': EntryAttributes.adult},
                '$addToSet': {f"settings.updates.{ctx.channel.id}": lst}
            }, 
            upsert=True)
        await ctx.send(f"This channel is now set to show {lst} updates")

    async def _disable_list(self, ctx, lst):
        doc = await Resources.guild_col.find_one({'guild_id': str(ctx.guild.id)}, {'settings.updates'})

        if not doc:
            return await ctx.send('This guild doesn\'t have updates')

        # remove lsit from channel settings
        try:
            doc['settings']['updates'][str(ctx.channel.id)].remove(lst)
        except:
            pass

        # remove channel if list empty
        try:
            if not doc['settings']['updates'][str(ctx.channel.id)]:
                del doc['settings']['updates'][str(ctx.channel.id)]
        except:
            pass

        await Resources.guild_col.update_one({'guild_id': str(ctx.guild.id)}, {'$set': {'settings.updates': doc['settings']['updates']}})

        await ctx.send(f"This channel will no longer show {lst} updates")

    async def _hide_updates(self, ctx, hide):
        user_id = str(ctx.author.id)
        new_status = UserStatus.CACHEONLY if hide else UserStatus.ACTIVE
        res = await Resources.user_col.update_many(
            { 'discord_id': user_id },
            {
                '$set': {
                    'status': new_status
                }
            }
        )
        if res.matched_count:
            for service in Resources.status_buffers:
                Resources.status_buffers[service][str(ctx.author.id)] = new_status
            if hide:
                await ctx.send(f"Success. Your list changes WILL NOT be displayed. (You will still show up in user portion of searches)")
            else:
                await ctx.send(f"Success. Your list changes WILL be displayed.")
        else:
            await ctx.send('Failure. User not found.')