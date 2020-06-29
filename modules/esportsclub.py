import random
import string
import discord

import os
import smtplib
from dotenv import load_dotenv

from .client import Client
from .user import User

bot = Client.bot
load_dotenv()

uwmadison = os.getenv("UWMADISON")
gmail_user = os.getenv("GMAILUSER")
gmail_pass = os.getenv("GMAILPASS")



class EsportsClub:

    @bot.command(pass_context=True)
    async def verify(ctx):
        asciiChars = string.ascii_lowercase + string.digits

        if uwmadison == "TRUE": #checks to see if UW Madison commands are enabled
            user = ctx.message.author

            s = ctx.message.content
            subcommand = s[9:14]

            if subcommand == "":
                await user.send("Type ``k!verify email [your @wisc.edu email]`` to verify your Discord account on the Esports Club Discord")
            elif subcommand == "email":
                content = s[15:]
                if "@wisc.edu" in content:
                    verificationCode = ''.join((random.choice(asciiChars) for i in range(4)))
                    print('Verification Code:'+verificationCode)
                    User.userUpdate(str(user.id), "VerificationCode", verificationCode)
                    print(content)

                    subject = "Esports Club Verification Code"
                    body = "To verify yourself with the Madison Esports Club, respond to the bot with the command \"k!verify code "+verificationCode+"\""

                    message = """From: %s
                    To: %s
                    Subject: %s

                    %s
                    """ % (gmail_user, ", ".join(content), subject, body)

                    try:
                        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                        server.ehlo()
                        server.login(gmail_user, gmail_pass)
                        server.sendmail(gmail_user, content, message)
                        server.close()

                        await user.send("An email has been sent to "+content+" with additional instructions!")
                        User.userUpdate(str(user.id), "Email", content)
                        print("Email sent to "+content)
                    except:
                        await user.send("An error has occured! You can attempt to verify again, or DM an admin on the server for help!")
                        print("Error with gmail login!")
                else:
                    await user.send("Be sure to use your ``@wisc.edu`` email address!")
            elif subcommand == "code ":
                content = s[14:]
                userCode = User.userRead(str(user.id), "VerificationCode")
                print(userCode)
                if content.lower() == userCode.lower():
                    try:
                        for guild in bot.guilds:
                            if str(guild.id) == "147255790078656513":
                                role = discord.utils.get(guild.roles, name='Verified')
                                await discord.Member.add_roles(member, role)
                        await user.send("Thank you, Verified role has been granted!")
                    except:
                        await user.send("Error granting role! DM an admin on the server for help!")
                else:
                    await user.send("The code does not match! Make sure you are copy-pasting the code correctly, and not including any additional characters such as spaces!")

            else:
                await ctx.send("Error, command not found!")

        else:
            await ctx.send("This command has been disabled!")
