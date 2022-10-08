import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks
import yt_dlp
import youtube_dl
import asyncio
from time import sleep
import os
import random

TOKEN = ""
playlist = []

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

help_command = commands.DefaultHelpCommand(
    no_category = 'Wow! Music commands!?!!'
)

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)
ytdl_old = youtube_dl.YoutubeDL(ytdl_format_options)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=['pog, ','p, '], intents=intents, help_command = help_command)

async def acutallyPlaySong(ctx):
	global vc
	while playlist != []:
		song = playlist[0]
		if not "/" in song:
			song = "https://youtu.be/"+song
		with ytdl as ydl:
			song_info = ydl.extract_info(song, download=False)
		r_url = song_info["formats"][3]["url"]
		
		if get(ctx.bot.voice_clients, guild=ctx.guild) == None:
			vc = await voice_channel.connect()
		vc.play(discord.FFmpegPCMAudio(r_url, **ffmpeg_options))
		while vc.is_playing():
			await asyncio.sleep(1)
		print("=====audio stopped playing=====")
		if ctx.bot.voice_clients == []:
			playlist.clear()
			break
		else:
			await skip(ctx)


@bot.command(help="youtube play command, only accepts url")
async def play(ctx, url: str):
	global playlist
	global voice_channel
	voice_channel = ctx.message.author.voice.channel
	if voice_channel != None:
		if '?list' in url:
			print("adding youtube playlist")
			full_command = f"yt-dlp {url} --get-id --flat-playlist"
			playlist += str(os.popen(full_command).read()).strip().split("\n")
			await queue(ctx)
		else:
			print("adding youtube video")
			playlist.append(url)
		playing = False
		try:
			if vc.is_playing():
				playing = True
		except:
			print("haha not playing")
		if not playing:
			await acutallyPlaySong(ctx)
	else:
		await ctx.send("gotta be in a voice channel bud")

@bot.command(help='stop playing and clear queue')
async def stop(ctx):
	vc.stop()
	await vc.disconnect()
	playlist = []

@bot.command(help='skips song')
async def skip(ctx):
	if voice_channel != None:
		vc.stop()
		playlist.pop(0)
		await acutallyPlaySong(ctx)
	else:
		await ctx.send("gotta be in a voice channel bud")

@bot.command(help='view youtube queue')
async def queue(ctx):
	q_msg = await ctx.send("Generating queue...")
	nplaylist = []
	short = 10
	if len(playlist)>10:
		additional = f"+{len(playlist)-10} more"
	else:
		short = len(playlist)
		additional = "The End."
	with ytdl as ydl:
		for i in range(short):
			try:
				nplaylist.append(ydl.extract_info(playlist[i], download=False).get('title',None))
			except:
				playlist.pop(i)
				playlist.insert(i, "https://www.youtube.com/watch?v=eoUkzOnNN1o")
				nplaylist.append("[POG! This video is private so its replaced with POG!]")
		for i in range(10-short):
			nplaylist.append("-")
	await q_msg.edit(content=f"""```		1 - {nplaylist[0]}
		2 - {nplaylist[1]}
		3 - {nplaylist[2]}
		4 - {nplaylist[3]}
		5 - {nplaylist[4]}
		6 - {nplaylist[5]}
		7 - {nplaylist[6]}
		8 - {nplaylist[7]}
		9 - {nplaylist[8]}
		10 - {nplaylist[9]}
		{additional}```""")

@bot.command(help='skip to a position')
async def skipto(ctx, pos: int):
	del playlist[:pos-2]
	await skip(ctx)
	await queue(ctx)

@bot.command(help='shuffle the playlist')
async def shuffle(ctx):
	firstSong = playlist.pop(0)
	random.shuffle(playlist)
	playlist.insert(0, firstSong)
	await queue(ctx)

@bot.command(help='places song next instead of at the end of a playlist')
async def playnext(ctx, url: str):
	if '?list' in url:
		ctx.send("Nah, not adding a whole playlist infront of another")
	else:
		await play(ctx, url)
	theSong = playlist.pop(len(playlist)-1)
	playlist.insert(1, theSong)



bot.run(TOKEN)