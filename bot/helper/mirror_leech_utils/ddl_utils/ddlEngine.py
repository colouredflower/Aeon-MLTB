#!/usr/bin/env python3
from io import BufferedReader
from json import JSONDecodeError
from pathlib import Path
from time import time
from traceback import format_exc

from aiofiles.os import path as aiopath
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ContentTypeError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from bot import LOGGER, user_data
from bot.core.config_manager import Config
from bot.helper.ext_utils.files_utils import get_mime_type_sync
from bot.helper.mirror_leech_utils.ddl_utils.ddlserver.gofile import Gofile
from bot.helper.mirror_leech_utils.ddl_utils.ddlserver.streamtape import Streamtape


class ProgressFileReader(BufferedReader):
    def __init__(self, filename, read_callback=None):
        super().__init__(open(filename, "rb"))
        self.__read_callback = read_callback
        self.length = Path(filename).stat().st_size

    def read(self, size=None):
        size = size or (self.length - self.tell())
        if self.__read_callback:
            self.__read_callback(self.tell())
        return super().read(size)


class DDLUploader:
    def __init__(self, listener=None, name=None, path=None):
        self.name = name
        self.__processed_bytes = 0
        self.last_uploaded = 0
        self.__listener = listener
        self.__path = path
        self.__start_time = time()
        self.total_files = 0
        self.total_folders = 0
        self.is_cancelled = False
        self.__is_errored = False
        self.__ddl_servers = {}
        self.__engine = "DDL v1"
        self.__asyncSession = None
        self.__user_id = self.__listener.message.from_user.id

    async def __user_settings(self):
        """Load DDL settings with user priority over owner settings"""
        user_dict = user_data.get(self.__user_id, {})

        # Helper function to get setting with user priority
        def get_ddl_setting(user_key, owner_attr, default_value=None):
            user_value = user_dict.get(user_key)
            if user_value is not None:
                return user_value
            return getattr(Config, owner_attr, default_value)

        # Get DDL server preference
        get_ddl_setting("DDL_SERVER", "DDL_DEFAULT_SERVER", "gofile")

        # Build DDL servers configuration
        self.__ddl_servers = {}

        # Gofile configuration
        gofile_api_key = get_ddl_setting("GOFILE_API_KEY", "GOFILE_API_KEY", "")
        gofile_enabled = bool(gofile_api_key)  # Enabled if API key is provided
        self.__ddl_servers["gofile"] = (gofile_enabled, gofile_api_key)

        # Streamtape configuration
        streamtape_login = get_ddl_setting(
            "STREAMTAPE_LOGIN", "STREAMTAPE_LOGIN", ""
        )
        streamtape_api_key = get_ddl_setting(
            "STREAMTAPE_API_KEY", "STREAMTAPE_API_KEY", ""
        )
        streamtape_enabled = bool(
            streamtape_login and streamtape_api_key
        )  # Enabled if both login and API key are provided
        # Combine login and API key for compatibility with existing code
        streamtape_credentials = (
            f"{streamtape_login}:{streamtape_api_key}" if streamtape_enabled else ""
        )
        self.__ddl_servers["streamtape"] = (
            streamtape_enabled,
            streamtape_credentials,
        )

    def __progress_callback(self, current):
        chunk_size = current - self.last_uploaded
        self.last_uploaded = current
        self.__processed_bytes += chunk_size

    @retry(
        wait=wait_exponential(multiplier=2, min=4, max=8),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(Exception),
    )
    async def upload_aiohttp(self, url, file_path, req_file, data):
        with ProgressFileReader(
            filename=file_path, read_callback=self.__progress_callback
        ) as file:
            data[req_file] = file
            # Set timeout for upload (30 minutes total, 5 minutes for connection)
            timeout = ClientTimeout(total=1800, connect=300)
            async with ClientSession(timeout=timeout) as self.__asyncSession:
                async with self.__asyncSession.post(url, data=data) as resp:
                    response_text = await resp.text()
                    LOGGER.info(f"DDL Upload Response Status: {resp.status}")

                    if resp.status == 200:
                        try:
                            return await resp.json()
                        except ContentTypeError:
                            LOGGER.info(
                                f"DDL Upload: Content type error, response: {response_text[:500]}"
                            )
                            return "Uploaded"
                        except JSONDecodeError:
                            LOGGER.error(
                                f"DDL Upload: JSON decode error, response: {response_text[:500]}"
                            )
                            return None
                    else:
                        LOGGER.error(
                            f"DDL Upload failed with status {resp.status}: {response_text[:500]}"
                        )
                        raise Exception(
                            f"Upload failed with HTTP {resp.status}: {response_text[:200]}"
                        )
                    return None

    async def __upload_to_ddl(self, file_path):
        all_links = {}
        for serv, (enabled, api_key) in self.__ddl_servers.items():
            if enabled:
                self.total_files = 0
                self.total_folders = 0
                if serv == "gofile":
                    self.__engine = "GoFile API"
                    nlink = await Gofile(self, api_key).upload(file_path)
                    all_links["GoFile"] = nlink
                if serv == "streamtape":
                    self.__engine = "StreamTape API"
                    try:
                        login, key = api_key.split(":")
                    except IndexError:
                        raise Exception(
                            "StreamTape Login & Key not Found, Kindly Recheck !"
                        )
                    nlink = await Streamtape(self, login, key).upload(file_path)
                    all_links["StreamTape"] = nlink
                self.__processed_bytes = 0
        if not all_links:
            raise Exception("No DDL Enabled to Upload.")
        return all_links

    async def upload(self, file_name, size):
        item_path = f"{self.__path}/{file_name}"
        LOGGER.info(f"Uploading: {item_path} via DDL")
        await self.__user_settings()
        try:
            if await aiopath.isfile(item_path):
                mime_type = get_mime_type_sync(item_path)
            else:
                mime_type = "Folder"
            link = await self.__upload_to_ddl(item_path)
            if link is None:
                raise Exception("Upload has been manually cancelled!")
            if self.is_cancelled:
                return
            LOGGER.info(f"Uploaded To DDL: {item_path}")
        except Exception as err:
            LOGGER.info("DDL Upload has been Cancelled")
            if self.__asyncSession:
                await self.__asyncSession.close()
            err = str(err).replace(">", "").replace("<", "")
            LOGGER.info(format_exc())
            await self.__listener.on_upload_error(err)
            self.__is_errored = True
        finally:
            if self.is_cancelled or self.__is_errored:
                return
            await self.__listener.on_upload_complete(
                link,
                size,
                self.total_files,
                self.total_folders,
                mime_type,
                file_name,
            )

    @property
    def speed(self):
        try:
            return self.__processed_bytes / int(time() - self.__start_time)
        except ZeroDivisionError:
            return 0

    @property
    def processed_bytes(self):
        return self.__processed_bytes

    @property
    def engine(self):
        return self.__engine

    async def cancel_download(self):
        self.is_cancelled = True
        LOGGER.info(f"Cancelling Upload: {self.name}")
        if self.__asyncSession:
            await self.__asyncSession.close()
        await self.__listener.on_upload_error("Your upload has been stopped!")
