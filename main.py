import discord
import os
import asyncio
import json
import secrets
from discord.ui import View
from discord.ext import commands
from discord.commands import Option
from SECRET import TOKEN
from CONFIG import SERVER

if os.name != "nt":
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    uvloop.install()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="^.^")

bot = Bot()
# load guild id from SERVER.py in CONFIG/
guild = SERVER.GUILD
# load admin role from SERVER.py in CONFIG/
admin = SERVER.ADMINROLE


@bot.listen()
async def on_ready():
    print(f"Bot online as {bot.user}.")

# Get winners
@bot.slash_command(name="getawinner", guild_ids=[guild], description="Roll the dice. Get a winner.")
@commands.has_role(admin)
async def getawinner(
    ctx: discord.ApplicationContext,
    noofwinners: Option(int, "Number of winners", min_value=1)
):
    await ctx.defer(ephemeral=True)
    # load local JSON database :: all participants
    with open("participants.json", 'r') as f:
        data = json.load(f)

    # helping variables
    l = []
    i = 0

    # while loop to go through json
    while(True):
        try:
            l.append(data["participant"+str(i)])
            i = i+1
        # exception -> end of json
        except(KeyError):
            # Check if selected number of winners is valid
            if noofwinners > len(l):
                await ctx.respond("Number for count of winners is higher than number of participants. Try again.", ephemeral=True)
                return

            await ctx.respond("Ended", ephemeral=True)

            # get winners

            for _ in range(0, noofwinners):
                winner = secrets.randbelow(len(l))

                # The winner is
                await ctx.channel.send(f"The winner is <@{l[winner-1]}>!")
            return

# Sub Class of View to participate
class Participate(View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    # Button
    @discord.ui.button(label="Participate", style=discord.ButtonStyle.green)
    async def button_callback(self, _, interaction):
        await interaction.response.defer(ephemeral=True)
        with open("participants.json", 'r') as f:
            data = json.load(f)

        # if user in json, end
        if str(interaction.user.id) in data.__str__():
            await interaction.followup.send("You have already participated!", ephemeral=True)
            return

        participants = data["participants"]

        data["participant"+str(participants)] = interaction.user.id
        data["participants"] = participants+1

        # write to file
        with open("participants.json", 'w') as f:
            json.dump(data, f)

        # participated successfully
        await interaction.followup.send(content="You have successfully registered!", ephemeral=True)

    async def on_timeout(self):
        pass

@bot.slash_command(name="createbutton", guild_ids=[guild], description="Create the giveaway button.")
@commands.has_role(admin)
async def createbutton(ctx: discord.ApplicationContext):
    view = Participate(ctx)
    await ctx.channel.send(content="Click the button to participate in the giveaway.", view=view)
    await ctx.respond("Button has been created successfully.", ephemeral=True)

# Load token from TOKEN.py in folder SECRET/
bot.run(TOKEN.TOKEN)
