import random
import re
import string
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
import requests
from requests_html import HTMLSession
import json

import os
import smtplib
from dotenv import load_dotenv

from modules.core.client import Client
from modules.config.user import User
from modules.cogs.configuration import Configuration
from modules.config.config import Config

load_dotenv()

gmail_user = os.getenv("GMAILUSER")
gmail_pass = os.getenv("GMAILPASS")

class EsportsClub(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def verify(self, ctx):
        asciiChars = string.ascii_lowercase + string.digits
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
                    #server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.ehlo()
                    server.starttls()
                    server.login(gmail_user, gmail_pass)
                except:
                    await user.send("An error has occured! You can attempt to verify again, or DM an admin on the server for help!")
                    print("Error with gmail login!")
                try:
                    server.sendmail(gmail_user, content, message)
                    server.close()

                    await user.send("An email has been sent to "+content+" with additional instructions!")
                    User.userUpdate(str(user.id), "Email", content)
                    print("Email sent to "+content)
                except:
                    await user.send("An error has occured! You can attempt to verify again, or DM an admin on the server for help!")
                    print("Error with sending the email!")
            else:
                await user.send("Be sure to use your ``@wisc.edu`` email address!")
        elif subcommand == "code ":
            content = s[14:]
            userCode = User.userRead(str(user.id), "VerificationCode")
            print(userCode)
            if content.lower() == userCode.lower():
                try:
                    for guild in self.bot.guilds:
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

    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def status(self, ctx):
        status = str(ctx.message.content)[(len(ctx.prefix) + len('config status ')):]
        try:
            Config.cfgUpdate(str(ctx.guild.id), "status", status)
        except:
            print("Error with changing status on Esports Club")
            pass
        try:
            esportsStatus = discord.Game(Config.cfgRead("147255790078656513", "status"))
        except:
            print("Error with changing status on Esports Club")
            pass
        await bot.change_presence(status=discord.Status.online, activity=esportsStatus)

    @commands.group()
    async def uw(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid UW command passed...')

    @uw.command(pass_context=True)
    async def search(self, ctx):
        contents = str(ctx.message.content)[(len(ctx.prefix) + len('uw search ')):]
        contentsReplaced = re.sub(r'\d', '#', contents)
        subj = contents[0:contentsReplaced.find('#')-1]
        num = int(contents[contentsReplaced.find('#'):len(contents)])

        subject = re.sub(r'[\s\-\_]', '', getAlias(subj))
        subjURL = getSubj(subject)
        course = getCourse(subjURL, num)
        if course==None:
            await ctx.send("No course with that ID found!")
        else:
            title = course.find('.courseblocktitle ', first=True).text
            credits = course.find('.courseblockcredits', first=True).text
            desc = course.find('.courseblockdesc', first=True).text
            extra = course.find('.cbextra-data', first=False)
            req = extra[0].text

            enroll = desc[desc.find('Enroll Info:')+12:len(desc)]
            desc = desc[0:desc.find('Enroll Info:')]

            if len(desc) > 512:
                length = 0
                periods = 0
                for char in desc:
                    length+=1
                    if char==".":
                        periods+=1
                        if periods==5:
                            break
                desc = desc[0:length]+" (Read more on course website)"

            titleShort = title[0:title.find("—")-1]
            subtitle = title[title.find("—")+2:len(title)]
            courseURL = "https://guide.wisc.edu/search/?P="+re.sub(r'\s', '%20', titleShort)

            embed = discord.Embed(
                title=subtitle,
                description=titleShort+" ("+credits[0]+"cr.)",
                url=courseURL,
                color=discord.Color(12911884)
            )

            embed.add_field(name="Description:", value=desc, inline=False)
            embed.add_field(name="Enroll info:", value=enroll, inline=False)
            embed.add_field(name="Repeatable:", value=extra[2].text, inline=True)
            embed.add_field(name="Last Taught:", value=extra[3].text, inline=True)
            embed.add_field(name="Requisites:", value=extra[0].text, inline=False)
            embed.add_field(name="Course Designation:", value=extra[1].text, inline=False)
            await ctx.send(embed=embed)

#super WIP code
def getSubj(subj):
    session = HTMLSession()
    r = session.get('https://guide.wisc.edu/courses/#text')
    links = r.html.absolute_links
    for link in links:
        #I feel like I need to apologize to God for this
        linkText=re.sub(r'_', '', str(link))
        if "/courses/"+subj in linkText:
            return link
    return None

def getCourse(url, num :int):
    session = HTMLSession()
    r = session.get(url)
    try:
        courses = r.html.find('.courseblock ', first=False)
    except Exception as e:
        print(e)
        return None
    numStr = str(num)+"</span>"
    for course in courses:
        if numStr in course.html:
            return course
    return None

def getAlias(subj):
    with open(os.getcwd()+"/modules/esports/subjAlias.json", "r") as alias_json:
        json_data = json.load(alias_json)

    for subject in json_data:
        for alias in subject["Alias"]:
            if alias.lower().startswith(subj):
                return subject["Course"]
    return subj
