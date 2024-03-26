import discord
from discord.ext import commands
import regex as re
import random
import FAQbot

""" 
Code for a discord bot, named Melbourne, made using the Discord_Bot_Template & Discord_Bot_Skeleton
by Sam Scott (Mohawk College, May 2023), implements the FAQbot script made by Mauricio Canul and
incorporates it to make a functional FAQ bot that can run and be interacted with through discord.

Mauricio Canul, January 2024
"""


class MyClient(discord.Client):

    def __init__(self):
        """
        Class initialization function, in order to build the base intents of the discord bot
        """
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        """
        Function triggered once the bot has started running and has connected to the discord API, prints a quirky message
        :return:
        """
        print(f'{self.user} says: God save the queen!')

    async def on_message(self, message):
        """
        Listener function to trigger any time a message is sent, if the user that sent it is
        the bot itself or another bot it stops, if it isn't then it proceeds, if Melbourne has
        been addressed with a "hello" it tries to process a response, if it hasn't but the message
        itself is "hello" then the bot will set itself as "addressed" (state = true) and say hi,
        if it is currently being addressed, but it is told "goodbye" then it stops being "addressed"
        it sends back any of the produced responses if there was one
        :param message: message that triggered the function
        :return:
        """
        if message.author == self.user or message.author.bot:
            return

        global state, response
        txt = message.content

        if state:
            if FAQbot.dismissMel(txt):
                response = "Bye bye!"
                state = False
            else:
                response = FAQbot.process(txt)
        elif FAQbot.greetMel(txt):
            response = "Hiya! How may I be of service?"
            state = True

        if response is not None:
            await message.channel.send(response.replace("\\n", "\n"))
            response = None


melBot = MyClient()
state = False
response = None

with open("TOKEN.txt") as file:
    token = file.read()

melBot.run(token)
