import discord
from discord.ext import commands
import os 
from keep_alive import keep_alive
keep_alive()
import random
import asyncio
import sqlite3
import requests

code = os.environ['bots']

log = 1238592413120069665
post = 1239311847035900029

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True


bot = commands.Bot(command_prefix='!', intents=intents)
#bot is on/status
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="!Help"))

# Banning a user
@bot.command()
async def ban(ctx, user: discord.Member, *, reason: str = "No reason provided"):
    # Ban the user
    await ctx.guild.ban(user, reason=reason)

   
    # Log the ban
    log_channel = bot.get_channel(log)
    if log_channel:
        embed = discord.Embed(title="User Banned", color=discord.Color.red())
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        await log_channel.send(embed=embed)

    # Send confirmation to the current channel
    await ctx.send(f"{user} has been banned for: {reason}")

    # Optionally, delete the command message
    await ctx.message.delete()

#unban by id and log it 
@bot.command()
async def unban(ctx, user_id: int):
    # Unban the user
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)

    # Log the unban
    log_channel = bot.get_channel(log)
    if log_channel:
        embed = discord.Embed(title="User Unbanned", color=discord.Color.green())
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        await log_channel.send(embed=embed)

    # Send confirmation to the current channel
    await ctx.send(f"{user} has been unbanned.")

    # Optionally, delete the command message
    await ctx.message.delete()    

# kick a user and log it
@bot.command()
async def kick(ctx, user: discord.Member, *, reason: str = "No reason provided"):
    # Kick the user
    await ctx.guild.kick(user, reason=reason)

    # Log the kick
    log_channel = bot.get_channel(log)
    if log_channel:
        embed = discord.Embed(title="User Kicked", color=discord.Color.orange())
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        await log_channel.send(embed=embed)

    # Send confirmation to the current channel
    await ctx.send(f"{user} has been kicked for: {reason}")

    # Optionally, delete the command message
    await ctx.message.delete()

#timeout a user and log it but we name it mute 
@bot.command()
async def mute(ctx, user: discord.Member, duration: int, *, reason: str = "No reason provided"):
    # Mute the user
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False)

    await user.add_roles(muted_role, reason=reason)

    # Log the mute
    log_channel = bot.get_channel(log)
    if log_channel:
        embed = discord.Embed(title="User Muted", color=discord.Color.orange())
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Duration", value=f"{duration} minute", inline=False)
        await log_channel.send(embed=embed)
    # Send confirmation to the current channel
    await ctx.send(f"{user} has been muted for {duration} minute for: {reason}")
    # Optionally, delete the command message
    await ctx.message.delete()
    # Schedule the unmute after the specified duration
    await asyncio.sleep(duration * 60)
    await user.remove_roles(muted_role)
    # Log the unmute
    if log_channel:
        embed = discord.Embed(title="User Unmuted", color=discord.Color.green())
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        await log_channel.send(embed=embed)
    # Send confirmation to the current channel
    await ctx.send(f"{user} has been unmuted.")    
    # Optionally, delete the command message
    await ctx.message.delete()


# Command: Post a message
@bot.command()
async def post(ctx, *, message):
    # Get the post channel
    post_channel = bot.get_channel(1239311847035900029)

    if post_channel:
        # Create an embedded message
        embed = discord.Embed(title="New Post", description=message, color=discord.Color.blue())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

        # Send the embedded message to the post channel
        post_message = await post_channel.send(embed=embed)

        # Delete the command message
        await ctx.message.delete()

        # Log the message
        await log_message(ctx.author, message, post_message)
    else:
        await ctx.send("Post channel not found.")

# Event: When a message is sent
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages sent by the bot itself

    # Log all messages (excluding command messages)
    if not message.content.startswith('!'):
        await log_message(message.author, message.content, message)

    # Check for inappropriate content and delete if necessary
    if contains_bad_word(message.content):
        await message.delete()
        await log_message(message.author, f"**DELETED MESSAGE:** {message.content}", None)

    await bot.process_commands(message)  # Ensure commands still work

# Function to log messages
async def log_message(author, content, post_message):
    log_channel = bot.get_channel(log)
    if log_channel:
        embed = discord.Embed(title="Message Log", color=discord.Color.blue())
        embed.add_field(name="Author", value=f"{author} ({author.id})", inline=False)
        embed.add_field(name="Content", value=content, inline=False)
        if post_message:
            embed.add_field(name="Posted Message", value=f"[Jump to Message]({post_message.jump_url})", inline=False)
        await log_channel.send(embed=embed)

# Function to check for bad words (customize this according to your needs)
def contains_bad_word(text):
    bad_words = ["badword1", "badword2"]  # List of bad words
    for word in bad_words:
        if word in text.lower():
            return True
    return False

#allclear commaned to clear all messages in the whole sever
@bot.command()
async def allclear(ctx):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge()
        await ctx.send("All messages have been cleared.")
    else:
        await ctx.send("You don't have permission to use this command.")

#clear command to clear messages in the current channel
@bot.command()
async def clear(ctx, amount: int):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"{amount} messages have been cleared.")
    else:
        await ctx.send("You don't have permission to use this command.")

#help cmmad to show all commands
@bot.command()
async def Help(ctx):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
    embed.add_field(name="!post", value="Post a message in the post channel.", inline=False)
    embed.add_field(name="!ban <user> [reason]", value="Ban a user.", inline=False)
    embed.add_field(name="!unban <user_id>", value="Unban a user.", inline=False)
    embed.add_field(name="!kick <user> [reason]", value="Kick a user.", inline=False)
    embed.add_field(name="!mute <user> <duration> [reason]", value="Mute a user." , inline=False)
    embed.add_field(name="!allclear", value="Clear all messages in the channel.", inline=False)
    embed.add_field(name="!clear <amount>", value="Clear a specified number of messages.", inline=False)
    embed.add_field(name="!Help", value="Show this help message.", inline=False)
    await ctx.send(embed=embed)
                
                
            

    









bot.run(code)