import os
import threading
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CHANNEL_ID = 1505991203014049982

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"Welcome {member.mention} to our cool server!")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    try:
        await member.ban(reason=reason)
        await ctx.send(f"Banned {member}. Reason: {reason}")
    except discord.Forbidden:
        await ctx.send("I don't have permission to ban that member.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    try:
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member}. Reason: {reason}")
    except discord.Forbidden:
        await ctx.send("I don't have permission to kick that member.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, seconds: int, *, reason="No reason"):
    try:
        until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
        await member.timeout(until, reason=reason)
        await ctx.send(f"Timed out {member} for {seconds} second(s). Reason: {reason}")
    except discord.Forbidden:
        await ctx.send("I don't have permission to timeout that member.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        cmd = ctx.command.name
        usage = {
            "timeout": "Usage: `!timeout @user <seconds> [reason]`",
            "ban": "Usage: `!ban @user [reason]`",
            "kick": "Usage: `!kick @user [reason]`",
        }
        await ctx.send(usage.get(cmd, f"Invalid argument. {error}"))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: `{error.param.name}`.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Member not found. Make sure you @mention them correctly.")

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise RuntimeError("DISCORD_TOKEN secret is not set")

bot.run(token)
