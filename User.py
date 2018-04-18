import discord
from discord.ext import commands

class User:
    def __init__(self, bot, database, soundboard):
        self.bot = bot
        self.database = database
        self.soundBoard = soundboard
        
    @commands.command(pass_context=True)
    async def admin(self, ctx, cmd : str, *params : str):
        val = self.database.GetFields("Users", ["ServerID", "UserID"], [ctx.message.server.id, ctx.message.author.id], ["Admin"])
        if val and val[0][0] == "True":
            if cmd == 'add':
                if len(params) >= 3 and params[0] == "sb":
                    if self.soundBoard.addCommand(ctx.message.server.id, params[1], params[2], params[3:]):
                        await self.bot.say("Added sb {}".format(params[1]))
                    else:
                        await self.bot.say("{} already exists as a command".format(param[1]))
                elif len(params) == 2 and params[0] == "admin":
                    if self.database.SetFields("Users", ["ServerID", "UserID"], [ctx.message.server.id, self.__stripId(params[1])], ["Admin"], ["True"]):
                        await self.bot.say("Added admin {}".format(params[1]))
            elif cmd == 'remove':
                if len(params) == 2 and params[0] == "sb":
                    if self.soundBoard.removeCommand(ctx.message.server.id, params[1]):
                        await self.bot.say("Removed sb {}".format(params[1]))
                elif len(params) == 2 and params[0] == "admin":
                    if self.database.SetFields("Users", ["ServerID", "UserID"], [ctx.message.server.id, self.__stripId(params[1])], ["Admin"], ["False"]):
                        await self.bot.say("Removed admin {}".format(params[1]))
            elif cmd == 'mute':
                if len(params) == 2 and params[0] == "sb":
                    if self.soundBoard.muteCommand(ctx.message.server.id, params[1], "True"):
                        await self.bot.say("Muted sb {}".format(params[1]))
                elif len(params) == 2 and params[0] == "user":
                    if self.database.SetFields("Users",  ["ServerID", "UserID"], [ctx.message.server.id, self.__stripId(params[1])], ["Mute"], ["True"]):
                        await self.bot.say("Muted user {}".format(params[1]))
            elif cmd == 'unmute':
                if len(params) == 2 and params[0] == "sb":
                    if self.soundBoard.muteCommand(ctx.message.server.id, params[1], "false"):
                        await self.bot.say("Unmuted sb {}".format(params[1]))
                elif len(params) == 2 and params[0] == "user":
                    if self.database.SetFields("Users", ["ServerID", "UserID"], [ctx.message.server.id, self.__stripId(params[1])], ["Mute"], ["False"]):
                        await self.bot.say("Unmuted user {}".format(params[1]))
            elif cmd == 'update':
                if len(params) >= 3 and params[0] == "whois":
                    if self.database.SetFields("Users", ["ServerID", "UserID"], [ctx.message.server.id, self.__stripId(params[1])], ["Iam"], [self.__combine_str(params[2:])]):
                        await self.bot.say("Updated user {}'s information".format(params[1]))
                elif len(params) >= 3 and params[0] == "sb":
                    if self.soundBoard.updateCommand(ctx.message.server.id, params[1], params[2:]):
                        await self.bot.say("Updated sb {}.".format(params[1]))
                    else:
                        await self.bot.say("Could not find command {}.".format(params[1]))
            else:
                await self.bot.say('Unknown Command')
        else:
            await self.bot.say("You are not an Admin!")
        
    @commands.command(pass_context=True)
    async def iam(self, ctx, *name : str):
        if self.database.SetFields("Users", ["ServerID", "UserID"], [ctx.message.server.id, ctx.message.author.id], ["Iam"], [self.__combine_str(name)]):
            await self.bot.say("I updated your information.")
        else:
            await self.bot.say("Something went wrong and I couldn't add you.")
            
    @commands.command(pass_context=True)
    async def whois(self, ctx, person : discord.Member):
        value = self.database.GetFields("Users", ["ServerID", "UserID"], [ctx.message.server.id, person.id], ["Iam"])
        if value:
            await self.bot.say(person.name + " is " + value[0][0] + ".")
        else:
            await self.bot.say("I do not know who " + person.name + " is.")
            
    async def on_member_join(self, member):
        if not self.database.FieldExists("Users", ["ServerID", "UserID"], [member.server.id, member.id]):
            print("Adding " + member.name)
            self.database.AddEntry("Users", ["ServerID", "UserID"], [member.server.id, member.id], ["Admin", "Mute", "Iam"], ["False", "False", ""])
    
    async def on_server_join(self, server):
        for s in server:
            for member in s.members:
                if not self.database.FieldExists("Users", ["ServerID", "UserID"], [s.id, member.id]):
                    if s.owner.id == member.id:
                        admin = "True"
                    else:
                        admin = "False"
                    self.database.AddEntry("Users", ["ServerID", "UserID"], [s.id, member.id], ["Admin", "Mute", "Iam"], [admin, "False", ""])
                        
    def __stripId(self, userId):
        return userId[2:-1]
        
    def __combine_str(self, strings):
        name = ''
        for x in strings:
            name += x + " "
        return name.strip()