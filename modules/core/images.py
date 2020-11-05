import io

async def get_profile_picture(session, user):
    """
    Get a bytes representation of a discord members profile picture
    """
    url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=128".format(user)
    async with session.get(url) as resp:
        return(io.BytesIO(await resp.content.read()))