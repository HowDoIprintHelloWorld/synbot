import os
import discord
import src.messages as ms
from random import randint
import json
import hashlib
from discord.utils import get
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

async def dmUser(user, message):
  dmChan = user.dm_channel
  if dmChan == None:
    dmChan = await user.create_dm()
  await dmChan.send(message)
  

def log(message):
  with open("data/log.txt", "a") as log:
   log.write(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]"+message)


async def timeOut(message):
  if not any([role for role in message.author.roles if any([r for r in ["Helper", "Mod", "Admin"] if r in str(role)])]):
    return
  server = client.get_guild(message.channel.guild.id)
  role = get(server.roles, name="❌ Timed-Out")
  user = message.mentions[0]
  await user.add_roles(role)
  oldRole = get(server.roles, name="member")
  await user.remove_roles(oldRole)
  log(f"User {str(user.name)} was timed out!")
  

async def checkChallenge(message):
  with open("data/challenges.json", "r") as file:
    data = json.load(file)
  if str(message.author) in data.keys():
    sol = data[str(message.author)]
    for i in range(50):
      sol = hashlib.md5(sol.encode())
      if i != 49:
        sol = str(sol.hexdigest())
        sol = sol[:11]
    if len(message.content.split()) >= 2:
      if message.content.split()[1] == str(sol.hexdigest()):
        await message.channel.send(ms.corrChall)
        server = client.get_guild(message.channel.guild.id)
        role = get(server.roles, name="verified (1/2)")
        await message.author.add_roles(role)
        return
    else:
      await message.channel.send(ms.challUsage)
      return
      
  else:
    await message.channel.send(ms.getChall)
    return
  
  await message.channel.send(ms.wrongChall)

async def verify(message):
  if "verify" not in str(message.channel):
    return
  chall = str(randint(10000, 1000000))
  
  with open("data/challenges.json", "r") as file:
    data = json.load(file)
  data[str(message.author)] = chall
  with open("data/challenges.json", "w") as file:
    json.dump(data, file)
  
  await message.channel.send(ms.verifyChall.replace("user",message.author.mention)+chall)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


async def getCommand(message):
  commands = {"verify":verify, "check-chall":checkChallenge, "time-out":timeOut}
  if len(message.content) > 1:
    command = message.content[1:].split()[0]
    if command in commands.keys():
      await commands[command](message)


@client.event
async def on_message(message):
  if message.author == client.user:
      return

  if message.content.startswith('!'):
      await getCommand(message)

@client.event
async def on_member_join(member):
  log(f"New member '{str(member.name)}' joined")

@client.event
async def on_member_remove(member):
  log(f"New member '{str(member.name)}' joined")

@client.event
async def on_member_update(before, after):
  print("Member updated")
  log(f"Member '{str(before)}' changed to '{str(after)}'")


@client.event
async def on_reaction_add(reaction, user):
  # TMP, CHANGE TO RULES ID
  if reaction.message.id == reaction.message.id:
    if "rules" in reaction.message.channel:
      if any(role for role in user.roles if role.name=="verified (1/2)"):
        server = client.get_guild(reaction.message.channel.guild.id)
        role = get(server.roles, name="member")
        await user.add_roles(role)
        oldRole = get(server.roles, name="verified (1/2)")
        await user.remove_roles(oldRole)
        await dmUser(user, ms.congratsJoining)

tok = os.environ['key']
client.run(tok)
