import os
import io
import re
import time
from datetime import datetime
from pathlib import Path

import stagger
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.errors.exceptions import FloodWait

from userge import userge, Config, Message
from userge.utils import sort_file_name_key, progress, take_screen_shot, humanbytes
from userge.utils.exceptions import ProcessCanceled
from userge.plugins.misc.download import tg_download, url_download

LOGGER = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)

LOGO_PATH = 'resources/userge.png'

from prime import PrimeUploads


# add command handler
@userge.on_cmd("pup", about={
    'header': "Upload files to primeuploads.com",
    'usage': "{tr}upload[file or folder path | link]",
    'examples': [
        "{tr}pup https://speed.hetzner.de/100MB.bin | test.bin",
        "{tr}pup downloads/test.mp4"]}, del_pre=True, check_downpath=True)

async def upload_to_pu(message: Message):
    """ upload to pu"""
    path_ = message.filtered_input_str
    if not path_:
        await message.err("Input not foud!")
        return
    is_url = re.search(r"(?:https?|ftp)://[^|\s]+\.[^|\s]+", path_)
    del_path = False
    if is_url:
        del_path = True
        try:
            path_, _ = await url_download(message, path_)
        except ProcessCanceled:
            await message.edit("`Process Canceled!`", del_in=5)
            return
        except Exception as e_e:  # pylint: disable=broad-except
            await message.err(str(e_e))
            return
    if "|" in path_:
        path_, file_name = path_.split("|")
        path_ = path_.strip()
        if os.path.isfile(path_):
            new_path = os.path.join(Config.DOWN_PATH, file_name.strip())
            os.rename(path_, new_path)
            path_ = new_path
    try:
        string = Path(path_)
    except IndexError:
        await message.err("wrong syntax")
    else:
        await message.delete()
        await PrimeUploads.login(key1="5LK1o2fqQdBdRoC2HDSmQE58O8GagL6RSXnonyLRVWzoisfOFbMXUbegy8EO2426", key2="GPklPmYOBtdc31Wmjn4nP8PWrfsikLP0SyIjn4iv1l1pM6uwOPXiL95UIQs8T2VE")
        await upload_pupath(message, string, del_path)

async def upload_pupath(message: Message, path: Path, del_path: bool):
    file_paths = []
    if path.exists():
        def explorer(_path: Path) -> None:
            if _path.is_file() and _path.stat().st_size:
                file_paths.append(_path)
            elif _path.is_dir():
                for i in sorted(_path.iterdir(), key=lambda a: sort_file_name_key(a.name)):
                    explorer(i)
        explorer(path)
    else:
        path = path.expanduser()
        str_path = os.path.join(*(path.parts[1:] if path.is_absolute() else path.parts))
        for p in Path(path.root).glob(str_path):
            file_paths.append(p)
    current = 0
    for p_t in file_paths:
        current += 1
        try:
            await PrimeUploads.upload(messsage, p_t, del_path, f"{current}/{len(file_paths)}")
        except FloodWait as f_e:
            time.sleep(f_e.x)  # asyncio sleep ?
        if message.process_is_canceled:
            break
