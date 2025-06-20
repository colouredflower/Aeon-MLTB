# ruff: noqa: RUF006
from asyncio import create_task, gather, sleep
from html import escape
from pathlib import Path

from aioshutil import move
from requests import utils as rutils

from bot import (
    DOWNLOAD_DIR,
    LOGGER,
    intervals,
    non_queued_dl,
    non_queued_up,
    queue_dict_lock,
    queued_dl,
    queued_up,
    same_directory_lock,
    task_dict,
    task_dict_lock,
)
from bot.core.aeon_client import TgClient
from bot.core.config_manager import Config
from bot.core.torrent_manager import TorrentManager
from bot.helper.common import TaskConfig
from bot.helper.ext_utils.aiofiles_compat import aiopath, listdir, makedirs, remove
from bot.helper.ext_utils.bot_utils import encode_slink, sync_to_async
from bot.helper.ext_utils.db_handler import database
from bot.helper.ext_utils.files_utils import (
    clean_download,
    clean_target,
    create_recursive_symlink,
    get_path_size,
    join_files,
    remove_excluded_files,
)
from bot.helper.ext_utils.links_utils import is_gdrive_id, is_rclone_path
from bot.helper.ext_utils.status_utils import get_readable_file_size
from bot.helper.ext_utils.task_manager import check_running_tasks, start_from_queued
from bot.helper.mirror_leech_utils.gdrive_utils.upload import GoogleDriveUpload
from bot.helper.mirror_leech_utils.rclone_utils.transfer import RcloneTransferHelper
from bot.helper.mirror_leech_utils.status_utils.gdrive_status import (
    GoogleDriveStatus,
)
from bot.helper.mirror_leech_utils.status_utils.queue_status import QueueStatus
from bot.helper.mirror_leech_utils.status_utils.rclone_status import RcloneStatus
from bot.helper.mirror_leech_utils.status_utils.telegram_status import TelegramStatus
from bot.helper.mirror_leech_utils.telegram_uploader import TelegramUploader
from bot.helper.mirror_leech_utils.youtube_utils.status import YouTubeStatus
from bot.helper.mirror_leech_utils.youtube_utils.upload import YouTubeUpload
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.telegram_helper.message_utils import (
    auto_delete_message,
    delete_links,
    delete_message,
    delete_status,
    send_message,
    update_status_message,
)


class TaskListener(TaskConfig):
    def __init__(self):
        super().__init__()

    async def clean(self):
        try:
            if st := intervals["status"]:
                for intvl in list(st.values()):
                    intvl.cancel()
            intervals["status"].clear()

            # Handle aria2 cleanup with better error handling
            try:
                await TorrentManager.aria2.purgeDownloadResult()
            except Exception as aria2_error:
                # Ignore transport closing errors as they're expected during cleanup
                if "closing transport" not in str(aria2_error).lower():
                    LOGGER.warning(f"Aria2 cleanup warning: {aria2_error}")

            await delete_status()
        except Exception as e:
            # Ignore transport closing errors as they're expected during cleanup
            if "closing transport" not in str(e).lower():
                LOGGER.error(e)

    def clear(self):
        self.subname = ""
        self.subsize = 0
        self.files_to_proceed = []
        self.proceed_count = 0
        self.progress = True

    async def _send_message_part(self, msg, fmsg):
        """Helper method to send a message part to appropriate destinations"""
        # Check if user specified a destination with -up flag
        if (
            self.up_dest
            and not is_gdrive_id(self.up_dest)
            and not is_rclone_path(self.up_dest)
        ):
            # If user specified a destination with -up flag, we need to send to all dump chats too
            # First, send to the specified destination
            try:
                # Send to the specified destination
                await send_message(
                    int(self.up_dest),
                    f"{msg}<blockquote expandable>{fmsg}</blockquote>",
                )
                # Also send to user's PM if it's not the same as the specified destination
                if int(self.up_dest) != self.user_id:
                    await send_message(
                        self.user_id,
                        f"{msg}<blockquote expandable>{fmsg}</blockquote>",
                    )

                # Send to user's dump if it's set and not the same as up_dest or user's PM
                user_dump = self.user_dict.get("USER_DUMP")
                if user_dump:
                    try:
                        user_dump_int = int(user_dump)
                        # Skip if this is the up_dest or user's PM (already sent there)
                        if (
                            user_dump_int != int(self.up_dest)
                            and user_dump_int != self.user_id
                        ):
                            LOGGER.info(
                                f"Sending task details message to user's dump: {user_dump}"
                            )
                            await send_message(
                                user_dump_int,
                                f"{msg}<blockquote expandable>{fmsg}</blockquote>",
                            )
                    except Exception as e:
                        LOGGER.error(
                            f"Failed to send task details message to user's dump {user_dump}: {e}"
                        )

                # Now send to all dump chats except the one specified with -up flag
                # Only use leech dump chats if leech operations are enabled
                if Config.LEECH_DUMP_CHAT and Config.LEECH_ENABLED:
                    if isinstance(Config.LEECH_DUMP_CHAT, list):
                        for chat_id in Config.LEECH_DUMP_CHAT:
                            processed_chat_id = chat_id

                            # Process the chat ID format (handle prefixes like b:, u:, h:)
                            if isinstance(processed_chat_id, str):
                                # Remove any prefixes like "b:", "u:", "h:" if present
                                if ":" in processed_chat_id:
                                    processed_chat_id = processed_chat_id.split(
                                        ":", 1
                                    )[1]

                                # Remove any suffixes after | if present (for hybrid format)
                                if "|" in processed_chat_id:
                                    processed_chat_id = processed_chat_id.split(
                                        "|", 1
                                    )[0]

                            # Skip if this is the up_dest (already sent there) or the user's PM
                            try:
                                processed_chat_id_int = int(processed_chat_id)
                                if (
                                    processed_chat_id_int == int(self.up_dest)
                                    or processed_chat_id_int == self.user_id
                                ):
                                    continue

                                # Skip if this is the user's dump (already sent there)
                                if user_dump and processed_chat_id_int == int(
                                    user_dump
                                ):
                                    continue

                                # Send to this dump chat
                                await send_message(
                                    processed_chat_id_int,
                                    f"{msg}<blockquote expandable>{fmsg}</blockquote>",
                                )
                            except Exception as e:
                                LOGGER.error(
                                    f"Failed to send task details message to dump chat {processed_chat_id}: {e}"
                                )
                    else:
                        # For backward compatibility with single chat ID
                        try:
                            # Skip if this is the up_dest, user's PM, or user's dump
                            if (
                                int(Config.LEECH_DUMP_CHAT) != int(self.up_dest)
                                and int(Config.LEECH_DUMP_CHAT) != self.user_id
                                and (
                                    not user_dump
                                    or int(Config.LEECH_DUMP_CHAT) != int(user_dump)
                                )
                            ):
                                LOGGER.info(
                                    f"Sending task details message to single dump chat: {Config.LEECH_DUMP_CHAT}"
                                )
                                await send_message(
                                    int(Config.LEECH_DUMP_CHAT),
                                    f"{msg}<blockquote expandable>{fmsg}</blockquote>",
                                )
                        except Exception as e:
                            LOGGER.error(
                                f"Failed to send task details message to single dump chat {Config.LEECH_DUMP_CHAT}: {e}"
                            )

            except Exception as e:
                LOGGER.error(
                    f"Failed to send leech log to specified destination {self.up_dest}: {e}"
                )
                # Fallback to user's PM
                await send_message(
                    self.user_id,
                    f"{msg}<blockquote expandable>{fmsg}</blockquote>",
                )
        else:
            # No specific destination was specified or it's a cloud destination
            # Determine leech destinations based on requirements
            leech_destinations = []

            # Only add user's PM for file details, not for task completion messages
            # We'll send the task completion message only to groups/supergroups
            leech_destinations.append(self.user_id)

            # Check if user has set their own dump and owner's premium status
            user_dump = self.user_dict.get("USER_DUMP")
            owner_has_premium = TgClient.IS_PREMIUM_USER

            # Case 1: If user didn't set any dump
            if not user_dump:
                # Send to leech dump chat and bot PM
                if Config.LEECH_DUMP_CHAT:
                    # Handle LEECH_DUMP_CHAT as a list
                    if isinstance(Config.LEECH_DUMP_CHAT, list):
                        for chat_id in Config.LEECH_DUMP_CHAT:
                            # Process the chat ID format (handle prefixes like b:, u:, h:)
                            if isinstance(chat_id, str):
                                # Remove any prefixes like "b:", "u:", "h:" if present
                                if ":" in chat_id:
                                    chat_id = chat_id.split(":", 1)[1]

                                # Remove any suffixes after | if present (for hybrid format)
                                if "|" in chat_id:
                                    chat_id = chat_id.split("|", 1)[0]

                            # Add to destinations
                            try:
                                leech_destinations.append(int(chat_id))
                            except ValueError:
                                # If it's not an integer (e.g., @username), add as is
                                leech_destinations.append(chat_id)
                    else:
                        # For backward compatibility with single chat ID
                        leech_destinations.append(int(Config.LEECH_DUMP_CHAT))

            # Case 2: If user set their own dump and owner has no premium string
            elif user_dump and not owner_has_premium:
                # Send to user's own dump, leech dump chat, and bot PM
                leech_destinations.append(int(user_dump))
                if Config.LEECH_DUMP_CHAT:
                    # Handle LEECH_DUMP_CHAT as a list
                    if isinstance(Config.LEECH_DUMP_CHAT, list):
                        for chat_id in Config.LEECH_DUMP_CHAT:
                            # Process the chat ID format (handle prefixes like b:, u:, h:)
                            if isinstance(chat_id, str):
                                # Remove any prefixes like "b:", "u:", "h:" if present
                                if ":" in chat_id:
                                    chat_id = chat_id.split(":", 1)[1]

                                # Remove any suffixes after | if present (for hybrid format)
                                if "|" in chat_id:
                                    chat_id = chat_id.split("|", 1)[0]

                            # Add to destinations
                            try:
                                leech_destinations.append(int(chat_id))
                            except ValueError:
                                # If it's not an integer (e.g., @username), add as is
                                leech_destinations.append(chat_id)
                    else:
                        # For backward compatibility with single chat ID
                        leech_destinations.append(int(Config.LEECH_DUMP_CHAT))

            # Case 3: If user set their own dump and owner has premium string
            elif user_dump and owner_has_premium:
                # By default, send to leech dump chat and bot PM
                if Config.LEECH_DUMP_CHAT:
                    # Handle LEECH_DUMP_CHAT as a list
                    if isinstance(Config.LEECH_DUMP_CHAT, list):
                        for chat_id in Config.LEECH_DUMP_CHAT:
                            # Process the chat ID format (handle prefixes like b:, u:, h:)
                            if isinstance(chat_id, str):
                                # Remove any prefixes like "b:", "u:", "h:" if present
                                if ":" in chat_id:
                                    chat_id = chat_id.split(":", 1)[1]

                                # Remove any suffixes after | if present (for hybrid format)
                                if "|" in chat_id:
                                    chat_id = chat_id.split("|", 1)[0]

                            # Add to destinations
                            try:
                                leech_destinations.append(int(chat_id))
                            except ValueError:
                                # If it's not an integer (e.g., @username), add as is
                                leech_destinations.append(chat_id)
                    else:
                        # For backward compatibility with single chat ID
                        leech_destinations.append(int(Config.LEECH_DUMP_CHAT))

                # Add user's dump to destinations regardless of premium status
                # This ensures task details are always sent to the user's dump
                try:
                    leech_destinations.append(int(user_dump))
                    LOGGER.info(
                        f"Adding user's dump {user_dump} to task details destinations"
                    )
                except Exception as e:
                    LOGGER.error(f"Error adding user's dump to destinations: {e}")

            # Remove duplicates while preserving order
            seen = set()
            leech_destinations = [
                x for x in leech_destinations if not (x in seen or seen.add(x))
            ]

            # Send to all destinations
            for dest in leech_destinations:
                try:
                    await send_message(
                        dest,
                        f"{msg}<blockquote expandable>{fmsg}</blockquote>",
                    )
                except Exception as e:
                    LOGGER.error(
                        f"Failed to send leech log to destination {dest}: {e}"
                    )

    async def remove_from_same_dir(self):
        async with task_dict_lock:
            if (
                self.folder_name
                and self.same_dir
                and self.mid in self.same_dir[self.folder_name]["tasks"]
            ):
                self.same_dir[self.folder_name]["tasks"].remove(self.mid)
                self.same_dir[self.folder_name]["total"] -= 1

    async def on_download_start(self):
        # Check if is_super_chat is a valid boolean attribute
        is_super_chat = (
            hasattr(self, "is_super_chat")
            and not callable(getattr(self, "is_super_chat", None))
            and self.is_super_chat
        )

        if is_super_chat and Config.INCOMPLETE_TASK_NOTIFIER and Config.DATABASE_URL:
            await database.add_incomplete_task(
                self.message.chat.id,
                self.message.link,
                self.tag,
            )

    async def on_download_complete(self):
        await sleep(2)
        if self.is_cancelled:
            LOGGER.info("Download was cancelled, skipping upload")
            return
        multi_links = False

        if (
            self.folder_name
            and self.same_dir
            and self.mid in self.same_dir[self.folder_name]["tasks"]
        ):
            LOGGER.info("Entering same_dir processing logic")
            async with same_directory_lock:
                while True:
                    async with task_dict_lock:
                        if self.mid not in self.same_dir[self.folder_name]["tasks"]:
                            return
                        if self.mid in self.same_dir[self.folder_name]["tasks"] and (
                            self.same_dir[self.folder_name]["total"] <= 1
                            or len(self.same_dir[self.folder_name]["tasks"]) > 1
                        ):
                            if self.same_dir[self.folder_name]["total"] > 1:
                                self.same_dir[self.folder_name]["tasks"].remove(
                                    self.mid,
                                )
                                self.same_dir[self.folder_name]["total"] -= 1
                                spath = f"{self.dir}{self.folder_name}"
                                des_id = next(
                                    iter(self.same_dir[self.folder_name]["tasks"]),
                                )
                                des_path = (
                                    f"{DOWNLOAD_DIR}{des_id}{self.folder_name}"
                                )
                                await makedirs(des_path, exist_ok=True)
                                LOGGER.info(
                                    f"Moving files from {self.mid} to {des_id}",
                                )
                                try:
                                    if not await aiopath.exists(spath):
                                        LOGGER.error(
                                            f"Source path does not exist: {spath}"
                                        )
                                        break

                                    items = await listdir(spath)
                                    for item in items:
                                        if item.strip().endswith((".aria2", ".!qB")):
                                            continue
                                        item_path = (
                                            f"{self.dir}{self.folder_name}/{item}"
                                        )

                                        try:
                                            des_items = await listdir(des_path)
                                            if item in des_items:
                                                await move(
                                                    item_path,
                                                    f"{des_path}/{self.mid}-{item}",
                                                )
                                            else:
                                                await move(
                                                    item_path, f"{des_path}/{item}"
                                                )
                                        except FileNotFoundError:
                                            LOGGER.error(
                                                f"Destination path does not exist: {des_path}"
                                            )
                                            # Try to create the directory again
                                            await makedirs(des_path, exist_ok=True)
                                            await move(
                                                item_path, f"{des_path}/{item}"
                                            )
                                        except Exception as e:
                                            LOGGER.error(
                                                f"Error moving file {item}: {e}"
                                            )
                                except FileNotFoundError:
                                    LOGGER.error(
                                        f"Source path does not exist: {spath}"
                                    )
                                    break
                                except Exception as e:
                                    LOGGER.error(
                                        f"Error listing directory {spath}: {e}"
                                    )
                                    break
                                multi_links = True
                            break
                    await sleep(1)
        else:
            pass

        async with task_dict_lock:
            if self.is_cancelled:
                return
            if self.mid in task_dict:
                download = task_dict[self.mid]
                self.name = download.name()
                gid = download.gid()
            else:
                return
        # Check directory contents immediately after download completion
        if await aiopath.exists(self.dir):
            try:
                files = await listdir(self.dir)
            except Exception as e:
                LOGGER.error(f"Error listing download directory: {e}")
        else:
            LOGGER.error(
                f"Download directory does not exist immediately after completion: {self.dir}"
            )

        if not (self.is_torrent or self.is_qbit):
            self.seed = False

        if multi_links:
            self.seed = False
            await self.on_upload_error(
                f"{self.name} Downloaded!\n\nWaiting for other tasks to finish...",
            )
            return

        if self.folder_name:
            self.name = self.folder_name.strip("/").split("/", 1)[0]

        # Check if this is a clone operation by looking at the task type
        is_clone_operation = hasattr(self, "is_clone") and self.is_clone
        if not is_clone_operation:
            # Also check if the name suggests it's a clone operation
            is_clone_operation = (
                hasattr(self, "name")
                and self.name
                and ("MEGA_File" in self.name or "clone" in str(self.name).lower())
            )

        if is_clone_operation:
            LOGGER.info(
                f"Clone operation detected - proceeding to upload phase for: {self.name}"
            )
            LOGGER.info(
                f"Clone operation - checking paths: dir={self.dir}, name={self.name}"
            )

            # For clone operations, we need to find the actual downloaded content
            # Try multiple path combinations to find the downloaded files
            possible_paths = [
                f"{self.dir}/{self.name}",  # Standard path
                self.dir,  # Direct directory
                f"{self.dir}",  # Just the directory
            ]

            dl_path = None
            for path in possible_paths:
                LOGGER.info(f"Clone operation - checking path: {path}")
                if await aiopath.exists(path):
                    dl_path = path
                    self.size = await get_path_size(path)
                    self.is_file = await aiopath.isfile(path)
                    LOGGER.info(
                        f"Clone operation - found downloaded content at: {path}"
                    )
                    break

            if not dl_path:
                # Last resort: check if files are in the download directory
                try:
                    LOGGER.info(
                        f"Clone operation - checking directory contents: {self.dir}"
                    )
                    LOGGER.info(
                        f"Clone operation - directory exists check: {await aiopath.exists(self.dir)}"
                    )

                    # Add a small delay to ensure any filesystem operations are complete
                    await sleep(1)
                    LOGGER.info(
                        f"Clone operation - directory exists after delay: {await aiopath.exists(self.dir)}"
                    )

                    if await aiopath.exists(self.dir):
                        files = await listdir(self.dir)
                        LOGGER.info(f"Clone operation - directory contents: {files}")
                        if files:
                            # Use the first file/folder found
                            self.name = files[0]
                            dl_path = f"{self.dir}/{self.name}"
                            self.size = await get_path_size(dl_path)
                            self.is_file = await aiopath.isfile(dl_path)
                            LOGGER.info(
                                f"Clone operation - using found content: {dl_path}"
                            )
                        else:
                            LOGGER.error(
                                f"Clone operation - directory exists but is empty: {self.dir}"
                            )
                            await self.on_upload_error(
                                f"Download directory is empty: {self.dir}"
                            )
                            return
                    else:
                        LOGGER.error(
                            f"Clone operation - download directory does not exist: {self.dir}"
                        )

                        # Check if there are any directories in the parent directory
                        parent_dir = str(Path(self.dir).parent)
                        LOGGER.info(
                            f"Clone operation - checking parent directory: {parent_dir}"
                        )
                        if await aiopath.exists(parent_dir):
                            try:
                                parent_files = await listdir(parent_dir)
                                LOGGER.info(
                                    f"Clone operation - parent directory contents: {parent_files}"
                                )

                                # Look for directories that might contain our download
                                for item in parent_files:
                                    item_path = f"{parent_dir}/{item}"
                                    if await aiopath.isdir(item_path):
                                        LOGGER.info(
                                            f"Clone operation - checking potential download dir: {item_path}"
                                        )
                                        try:
                                            item_contents = await listdir(item_path)
                                            LOGGER.info(
                                                f"Clone operation - {item_path} contents: {item_contents}"
                                            )
                                        except Exception as e:
                                            LOGGER.info(
                                                f"Clone operation - error checking {item_path}: {e}"
                                            )
                            except Exception as e:
                                LOGGER.error(
                                    f"Clone operation - error checking parent directory: {e}"
                                )

                        await self.on_upload_error(
                            f"Download directory does not exist: {self.dir}"
                        )
                        return
                except Exception as e:
                    LOGGER.error(
                        f"Clone operation - error checking download directory: {e}"
                    )
                    await self.on_upload_error(
                        f"Error checking download directory: {e}"
                    )
                    return
        else:
            # Normal file/directory processing for non-clone operations
            if not await aiopath.exists(f"{self.dir}/{self.name}"):
                try:
                    # Check if directory exists before listing
                    if not await aiopath.exists(self.dir):
                        LOGGER.error(f"Directory does not exist: {self.dir}")
                        await self.on_upload_error(
                            f"Directory does not exist: {self.dir}"
                        )
                        return

                    files = await listdir(self.dir)
                    if not files:
                        LOGGER.error(f"Directory is empty: {self.dir}")
                        await self.on_upload_error(f"Directory is empty: {self.dir}")
                        return

                    self.name = files[-1]
                    if self.name == "yt-dlp-thumb":
                        if len(files) > 1:
                            self.name = files[0]
                        else:
                            LOGGER.error(
                                f"No valid files found in directory: {self.dir}"
                            )
                            await self.on_upload_error(
                                f"No valid files found in directory: {self.dir}"
                            )
                            return
                except FileNotFoundError:
                    LOGGER.error(f"Directory does not exist: {self.dir}")
                    await self.on_upload_error(
                        f"Directory does not exist: {self.dir}"
                    )
                    return
                except Exception as e:
                    LOGGER.error(f"Error listing directory {self.dir}: {e}")
                    await self.on_upload_error(str(e))
                    return

            dl_path = f"{self.dir}/{self.name}"
            self.size = await get_path_size(dl_path)
            self.is_file = await aiopath.isfile(dl_path)

        # Set upload paths based on operation type
        if is_clone_operation:
            # For clone operations, use the actual downloaded file/folder path
            up_dir = self.dir
            up_path = dl_path  # Use the dl_path we determined above
        elif self.seed:
            up_dir = self.up_dir = f"{self.dir}10000"
            up_path = f"{self.up_dir}/{self.name}"
            await create_recursive_symlink(self.dir, self.up_dir)
            LOGGER.info(f"Shortcut created: {dl_path} -> {up_path}")
        else:
            up_dir = self.dir
            up_path = dl_path
        await remove_excluded_files(
            self.up_dir or self.dir,
            self.excluded_extensions,
        )
        if not Config.QUEUE_ALL:
            async with queue_dict_lock:
                if self.mid in non_queued_dl:
                    non_queued_dl.remove(self.mid)
            await start_from_queued()

        if self.join and not self.is_file:
            await join_files(up_path)

        # Check if archive flags are enabled in config
        from bot.helper.ext_utils.bot_utils import is_flag_enabled

        if self.extract and not self.is_nzb and is_flag_enabled("-e"):
            up_path = await self.proceed_extract(up_path, gid)
            if self.is_cancelled:
                return
            self.is_file = await aiopath.isfile(up_path)
            self.name = up_path.replace(f"{up_dir}/", "").split("/", 1)[0]
            self.size = await get_path_size(up_dir)
            self.clear()
            await remove_excluded_files(up_dir, self.excluded_extensions)

        # Determine which media tool to run first based on priority
        media_tools = []

        if self.merge_enabled:
            media_tools.append((self.merge_priority, "merge", self.proceed_merge))

        # Check if watermark is enabled AND watermark text is available
        if self.watermark_enabled and self.watermark:
            media_tools.append(
                (self.watermark_priority, "watermark", self.proceed_watermark)
            )

        # Check if trim is enabled or trim parameters are provided
        if self.trim_enabled or self.trim:
            media_tools.append((self.trim_priority, "trim", self.proceed_trim))

        # Check if compression is enabled
        if self.compression_enabled:
            media_tools.append(
                (self.compression_priority, "compression", self.proceed_compress)
            )

        # Check if extract is enabled
        if self.extract_enabled:
            media_tools.append(
                (self.extract_priority, "extract", self.proceed_extract_tracks)
            )

        # Check if remove is enabled
        if self.remove_enabled:
            media_tools.append(
                (self.remove_priority, "remove", self.proceed_remove_tracks)
            )

        # Check if add is enabled
        if self.add_enabled:
            media_tools.append((self.add_priority, "add", self.proceed_add))

        # Sort media tools by priority (lower number = higher priority)
        media_tools.sort(key=lambda x: x[0])

        # Run media tools in priority order
        for _, tool_name, tool_func in media_tools:
            LOGGER.info(f"Running {tool_name} with priority {_}")
            up_path = await tool_func(up_path, gid)
            if self.is_cancelled:
                return
            self.is_file = await aiopath.isfile(up_path)
            self.name = up_path.replace(f"{up_dir}/", "").split("/", 1)[0]
            self.size = await get_path_size(up_dir)
            self.clear()

        # Check if any metadata settings are provided (legacy or new)
        if (
            self.metadata
            or self.metadata_title
            or self.metadata_author
            or self.metadata_comment
            or self.metadata_all
            or self.metadata_video_title
            or self.metadata_video_author
            or self.metadata_video_comment
            or self.metadata_audio_title
            or self.metadata_audio_author
            or self.metadata_audio_comment
            or self.metadata_subtitle_title
            or self.metadata_subtitle_author
            or self.metadata_subtitle_comment
        ):
            up_path = await self.proceed_metadata(
                up_path,
                gid,
            )
            if self.is_cancelled:
                return
            self.is_file = await aiopath.isfile(up_path)
            self.name = up_path.replace(f"{up_dir}/", "").split("/", 1)[0]
            self.size = await get_path_size(up_dir)
            self.clear()

        if self.ffmpeg_cmds:
            up_path = await self.proceed_ffmpeg(
                up_path,
                gid,
            )
            if self.is_cancelled:
                return
            self.is_file = await aiopath.isfile(up_path)
            self.name = up_path.replace(f"{up_dir}/", "").split("/", 1)[0]
            self.size = await get_path_size(up_dir)
            self.clear()

        if self.name_sub:
            up_path = await self.substitute(up_path)
            if self.is_cancelled:
                return
            self.is_file = await aiopath.isfile(up_path)
            self.name = up_path.replace(f"{up_dir}/", "").split("/", 1)[0]

        up_path = await self.remove_www_prefix(up_path)
        self.is_file = await aiopath.isfile(up_path)
        self.name = up_path.replace(f"{up_dir}/", "").split("/", 1)[0]

        # Apply universal filename for mirror files (if not leech and no -n flag was used)
        if not self.is_leech:
            up_path = await self.apply_universal_filename(up_path, up_dir)
            if self.is_cancelled:
                return
            self.is_file = await aiopath.isfile(up_path)
            self.name = up_path.replace(f"{up_dir}/", "").split("/", 1)[0]

        if self.screen_shots:
            up_path = await self.generate_screenshots(up_path)
            if self.is_cancelled:
                return
            self.is_file = await aiopath.isfile(up_path)
            self.name = up_path.replace(f"{up_dir}/", "").split("/", 1)[0]
            self.size = await get_path_size(up_dir)

        if self.convert_audio or self.convert_video:
            up_path = await self.convert_media(
                up_path,
                gid,
            )
            if self.is_cancelled:
                return
            self.is_file = await aiopath.isfile(up_path)
            self.name = up_path.replace(f"{up_dir}/", "").split("/", 1)[0]
            self.size = await get_path_size(up_dir)
            self.clear()

        if self.sample_video:
            up_path = await self.generate_sample_video(
                up_path,
                gid,
            )
            if self.is_cancelled:
                return
            self.is_file = await aiopath.isfile(up_path)
            self.name = up_path.replace(f"{up_dir}/", "").split("/", 1)[0]
            self.size = await get_path_size(up_dir)
            self.clear()

        # Add direct compression handling for -z flag if not already handled by media tools
        # Check if archive flags are enabled in config using is_flag_enabled

        if self.compress and not self.compression_enabled and is_flag_enabled("-z"):
            LOGGER.info(f"Direct compression triggered by -z flag for: {self.name}")
            up_path = await self.compress_with_7z(up_path, gid)
            if self.is_cancelled:
                return
            self.is_file = await aiopath.isfile(up_path)
            self.name = up_path.replace(f"{up_dir}/", "").split("/", 1)[0]
            self.size = await get_path_size(up_dir)
            self.clear()

        self.name = up_path.replace(f"{up_dir}/", "").split("/", 1)[0]
        self.size = await get_path_size(up_dir)

        if self.is_leech:
            await self.proceed_split(
                up_path,
                gid,
            )
            if self.is_cancelled:
                return
            self.clear()

        self.subproc = None

        # Store MediaInfo link for later use in task completion message
        self.mediainfo_link = None

        add_to_queue, event = await check_running_tasks(self, "up")
        await start_from_queued()
        if add_to_queue:
            LOGGER.info(f"Added to Queue/Upload: {self.name}")
            async with task_dict_lock:
                task_dict[self.mid] = QueueStatus(self, gid, "Up")
            await event.wait()
            if self.is_cancelled:
                return
            LOGGER.info(f"Start from Queued/Upload: {self.name}")

        self.size = await get_path_size(up_dir)

        # For mirror tasks, send the command message to log chat ID if configured
        self.log_msg = None
        if not self.is_leech and Config.LOG_CHAT_ID:
            try:
                msg = self.message.text.lstrip("/")
                # Send command message to log chat ID
                self.log_msg = await self.client.send_message(
                    chat_id=int(Config.LOG_CHAT_ID),
                    text=msg,
                    disable_web_page_preview=True,
                    disable_notification=True,
                )

            except Exception:
                pass

        if self.is_leech:
            LOGGER.info(f"Leech Name: {self.name}")
            tg = TelegramUploader(self, up_dir)
            # Store a reference to the telegram uploader for later use (e.g., during cancellation)
            self.telegram_uploader = tg
            async with task_dict_lock:
                task_dict[self.mid] = TelegramStatus(self, tg, gid, "up")
            await gather(
                update_status_message(self.message.chat.id),
                tg.upload(),
            )
            # We don't want to delete the command messages in dump chats anymore
            # This was causing the auto-deleted command messages issue
            # Instead, we'll keep them for reference
            if (hasattr(tg, "dump_chat_msgs") and tg.dump_chat_msgs) or (
                hasattr(tg, "log_msg") and tg.log_msg
            ):
                pass

            # Delete the original command message if it's not in the dump chats list
            # This prevents duplicate command messages
            if (
                self.message
                and self.message.chat
                and self.message.chat.type != "private"
            ):
                # Check if the original chat is in the dump chats list
                original_chat_id = str(self.message.chat.id)
                original_chat_in_dump = False

                if hasattr(tg, "dump_chat_msgs") and tg.dump_chat_msgs:
                    for chat_id in tg.dump_chat_msgs:
                        processed_chat_id = chat_id

                        # Process the chat ID format (handle prefixes like b:, u:, h:)
                        if isinstance(processed_chat_id, str):
                            # Remove any prefixes like "b:", "u:", "h:" if present
                            if ":" in processed_chat_id:
                                processed_chat_id = processed_chat_id.split(":", 1)[
                                    1
                                ]

                            # Remove any suffixes after | if present (for hybrid format)
                            if "|" in processed_chat_id:
                                processed_chat_id = processed_chat_id.split("|", 1)[
                                    0
                                ]

                        # Check if the processed chat ID matches the original chat ID (handle different formats)
                        if (
                            str(processed_chat_id) == original_chat_id
                            or (
                                original_chat_id.startswith("-100")
                                and str(processed_chat_id) == original_chat_id[4:]
                            )
                            or (
                                not original_chat_id.startswith("-100")
                                and f"-100{original_chat_id}"
                                == str(processed_chat_id)
                            )
                        ):
                            original_chat_in_dump = True
                            break

                # If the original chat is not in the dump chats list, delete the command message
                if not original_chat_in_dump:
                    try:
                        await delete_message(self.message)
                    except Exception as e:
                        LOGGER.error(
                            f"Failed to delete command message in original chat: {e}"
                        )
            # Don't delete the tg reference as we need it for cancellation
            # We'll keep the reference in self.telegram_uploader
        elif self.up_dest == "yt" or self.up_dest.startswith("yt:"):
            # YouTube upload
            if not getattr(Config, "YOUTUBE_UPLOAD_ENABLED", False):
                await self.on_upload_error(
                    "YouTube upload is disabled by administrator"
                )
                return

            LOGGER.info(f"YouTube Upload Name: {self.name}")

            # For YouTube mirror tasks, send the command message to log chat ID if configured
            if not self.is_leech and Config.LOG_CHAT_ID:
                try:
                    msg = self.message.text.lstrip("/")
                    # Send command message to log chat ID
                    await self.client.send_message(
                        chat_id=int(Config.LOG_CHAT_ID),
                        text=msg,
                        disable_web_page_preview=True,
                        disable_notification=True,
                    )
                except Exception:
                    pass

            youtube_upload = YouTubeUpload(self, up_path)

            # Parse YouTube-specific parameters from up_dest
            if self.up_dest.startswith("yt:"):
                # Format: yt:privacy:category:tags:title
                # Example: yt:unlisted:22:music,video:My Custom Title
                parts = self.up_dest.split(":")
                if len(parts) > 1 and parts[1]:
                    youtube_upload.privacy_status = parts[1]
                if len(parts) > 2 and parts[2]:
                    youtube_upload.category_id = parts[2]
                if len(parts) > 3 and parts[3]:
                    youtube_upload.default_tags = parts[3]
                if len(parts) > 4 and parts[4]:
                    # Custom title provided via command line
                    youtube_upload.custom_title = parts[4]

            async with task_dict_lock:
                task_dict[self.mid] = YouTubeStatus(self, youtube_upload, gid, "up")
            await gather(
                update_status_message(self.message.chat.id),
                sync_to_async(youtube_upload.upload),
            )
            del youtube_upload
        elif self.up_dest == "mg":
            # Import here to avoid circular imports
            from bot.helper.mirror_leech_utils.mega_utils.upload import (
                add_mega_upload,
            )

            # Check if MEGA upload is enabled
            if not Config.MEGA_UPLOAD_ENABLED:
                await self.on_upload_error(
                    "❌ MEGA upload is disabled by the administrator."
                )
                return

            # Check if MEGA credentials are configured (user or bot-wide)
            user_mega_email = self.user_dict.get("MEGA_EMAIL")
            user_mega_password = self.user_dict.get("MEGA_PASSWORD")

            has_user_credentials = user_mega_email and user_mega_password
            has_bot_credentials = Config.MEGA_EMAIL and Config.MEGA_PASSWORD

            if not has_user_credentials and not has_bot_credentials:
                await self.on_upload_error(
                    "❌ MEGA credentials not configured. Please set your MEGA credentials in /settings → MEGA Settings or contact the administrator."
                )
                return

            await add_mega_upload(self, up_path)
        elif self.up_dest == "ddl" or self.up_dest.startswith("ddl:"):
            # DDL upload using DDL engine
            from bot.helper.common import validate_ddl_config
            from bot.helper.mirror_leech_utils.ddl_utils.ddlEngine import DDLUploader
            from bot.helper.mirror_leech_utils.status_utils.ddl_status import (
                DDLStatus,
            )

            # Validate DDL configuration
            is_valid, error_msg = validate_ddl_config(self.user_id)
            if not is_valid:
                await self.on_upload_error(error_msg)
                return

            LOGGER.info(f"DDL Upload Name: {self.name}")
            size = await get_path_size(up_path)
            ddl = DDLUploader(self, self.name, up_dir)
            async with task_dict_lock:
                task_dict[self.mid] = DDLStatus(ddl, size, self.message, gid, None)
            await gather(
                update_status_message(self.message.chat.id),
                ddl.upload(self.name, size),
            )
            del ddl
        elif is_gdrive_id(self.up_dest) or self.up_dest == "gd":
            # Check if Google Drive upload is enabled
            if not Config.GDRIVE_UPLOAD_ENABLED:
                await self.on_upload_error(
                    "❌ Google Drive upload is disabled by the administrator."
                )
                return

            LOGGER.info(f"Gdrive Upload Name: {self.name}")
            # If up_dest is "gd", use the configured GDRIVE_ID
            if self.up_dest == "gd":
                gdrive_id = self.user_dict.get("GDRIVE_ID") or Config.GDRIVE_ID
                if gdrive_id:
                    self.up_dest = gdrive_id
                else:
                    LOGGER.warning(
                        "DEFAULT_UPLOAD is 'gd' but no GDRIVE_ID configured, falling back to Rclone"
                    )
                    LOGGER.info(f"Rclone Upload Name: {self.name}")
                    RCTransfer = RcloneTransferHelper(self)
                    async with task_dict_lock:
                        task_dict[self.mid] = RcloneStatus(
                            self, RCTransfer, gid, "up"
                        )
                    await gather(
                        update_status_message(self.message.chat.id),
                        RCTransfer.upload(up_path),
                    )
                    del RCTransfer
                    return

            drive = GoogleDriveUpload(self, up_path)
            async with task_dict_lock:
                task_dict[self.mid] = GoogleDriveStatus(self, drive, gid, "up")
            await gather(
                update_status_message(self.message.chat.id),
                sync_to_async(drive.upload),
            )
            del drive
        else:
            LOGGER.info(f"Rclone Upload Name: {self.name}")
            RCTransfer = RcloneTransferHelper(self)
            async with task_dict_lock:
                task_dict[self.mid] = RcloneStatus(self, RCTransfer, gid, "up")
            await gather(
                update_status_message(self.message.chat.id),
                RCTransfer.upload(up_path),
            )
            del RCTransfer
        return

    async def on_upload_complete(
        self,
        link,
        files,
        folders,
        mime_type,
        rclone_path="",
        dir_id="",
    ):
        # Check if is_super_chat is a valid boolean attribute
        is_super_chat = (
            hasattr(self, "is_super_chat")
            and not callable(getattr(self, "is_super_chat", None))
            and self.is_super_chat
        )

        if is_super_chat and Config.INCOMPLETE_TASK_NOTIFIER and Config.DATABASE_URL:
            await database.rm_complete_task(self.message.link)

        # Use the most up-to-date name (which may have been modified by leech filename template)
        current_name = self.name

        # Check if MediaInfo is enabled
        mediainfo_enabled = self.user_dict.get("MEDIAINFO_ENABLED", None)
        if mediainfo_enabled is None:
            mediainfo_enabled = Config.MEDIAINFO_ENABLED

        # If this is a leech task and files is a dictionary (from TelegramUploader)
        if self.is_leech and isinstance(files, dict) and files:
            # Get the first file's name from the dictionary values
            first_file = next(iter(files.values()), None)
            if first_file:
                # Use the actual filename that was uploaded
                current_name = first_file
                # Remove part numbers from the filename if present
                import re

                if re.search(r"\.part\d+(\..*)?$", current_name):
                    base_name = re.sub(r"\.part\d+(\..*)?$", "", current_name)
                    ext = current_name.split(".")[-1] if "." in current_name else ""
                    current_name = f"{base_name}.{ext}" if ext else base_name

        # Truncate name if too long to prevent message length issues
        display_name = current_name
        if len(display_name) > 100:
            display_name = display_name[:97] + "..."

        msg = f"<b>Name: </b><code>{escape(display_name)}</code>\n\n<blockquote><b>Size: </b>{get_readable_file_size(self.size)}"
        done_msg = f"<b><blockquote>Hey, {self.tag}</blockquote>\nYour task is complete\nPlease check your inbox.</b>"
        LOGGER.info(f"Task Done: {current_name}")
        if self.is_leech:
            msg += f"\n<b>Total Files: </b>{folders}"
            if mime_type != 0:
                msg += f"\n<b>Corrupted Files: </b>{mime_type}"
            msg += f"\n<b>cc: </b>{self.tag}"

            # Add media store links inside blockquote if enabled and there's only one file
            # Check if Media Store is enabled for this user
            user_media_store_enabled = self.user_dict.get("MEDIA_STORE", None)
            if user_media_store_enabled is None:
                user_media_store_enabled = Config.MEDIA_STORE
            if user_media_store_enabled and files and len(files) == 1:
                url = next(iter(files.keys()))
                chat_id, msg_id = url.split("/")[-2:]
                if chat_id.isdigit():
                    chat_id = f"-100{chat_id}"
                store_link = f"https://t.me/{TgClient.NAME}?start={encode_slink('file' + chat_id + '&&' + msg_id)}"
                msg += f"\n\n<b>Media Links:</b>\n┖ <a href='{store_link}'>Store Link</a> | <a href='https://t.me/share/url?url={store_link}'>Share Link</a>"

                # Add MediaInfo link if it was generated before upload
                user_mediainfo_enabled = self.user_dict.get(
                    "MEDIAINFO_ENABLED", None
                )
                if user_mediainfo_enabled is None:
                    user_mediainfo_enabled = (
                        Config.MEDIAINFO_ENABLED
                    )  # Use the pre-generated MediaInfo link if available
                if (
                    user_mediainfo_enabled
                    and hasattr(self, "mediainfo_link")
                    and self.mediainfo_link
                ):
                    msg += f"\n┖ <b>MediaInfo</b> → <a href='https://graph.org/{self.mediainfo_link}'>View</a>"

            msg += "</blockquote>\n\n"

            if not files:
                await send_message(self.message, msg)
            else:
                # Convert files dict to list for easier processing
                files_list = list(files.items())
                total_files = len(files_list)

                # Process files in chunks, ensuring at least 10 files per message
                file_index = 0
                message_parts = []

                while file_index < total_files:
                    fmsg = ""
                    files_in_current_message = 0
                    start_index = file_index

                    # Build message with files, ensuring minimum 10 files per message
                    while file_index < total_files:
                        url, name = files_list[file_index]
                        current_file_number = file_index + 1

                        # Build complete file entry
                        file_entry = ""

                        # Truncate file name if too long
                        display_file_name = name
                        if len(display_file_name) > 80:
                            display_file_name = display_file_name[:77] + "..."
                        file_entry += f"{current_file_number}. <a href='{url}'>{display_file_name}</a>"

                        # Add store link if enabled
                        # Check if Media Store is enabled for this user
                        user_media_store_enabled = self.user_dict.get(
                            "MEDIA_STORE", None
                        )
                        if user_media_store_enabled is None:
                            user_media_store_enabled = Config.MEDIA_STORE
                        if user_media_store_enabled:
                            chat_id, msg_id = url.split("/")[-2:]
                            if chat_id.isdigit():
                                chat_id = f"-100{chat_id}"
                            store_link = f"https://t.me/{TgClient.NAME}?start={encode_slink('file' + chat_id + '&&' + msg_id)}"
                            file_entry += f"\n┖ <b>Get Media</b> → <a href='{store_link}'>Store Link</a> | <a href='https://t.me/share/url?url={store_link}'>Share Link</a>"

                        # Add MediaInfo link for media files if enabled
                        # Check if MediaInfo is enabled for this user
                        user_mediainfo_enabled = self.user_dict.get(
                            "MEDIAINFO_ENABLED", None
                        )
                        if user_mediainfo_enabled is None:
                            user_mediainfo_enabled = Config.MEDIAINFO_ENABLED  # Use the pre-generated MediaInfo link if available and valid
                        if (
                            user_mediainfo_enabled
                            and hasattr(self, "mediainfo_link")
                            and self.mediainfo_link
                            and self.mediainfo_link.strip()
                        ):
                            # Support all media types including archives, documents, images, etc.
                            file_entry += f"\n┖ <b>MediaInfo</b> → <a href='https://graph.org/{self.mediainfo_link}'>View</a>"
                            # Log that MediaInfo link was successfully added to the message
                        elif user_mediainfo_enabled and hasattr(
                            self, "mediainfo_link"
                        ):
                            # MediaInfo was attempted but failed or returned empty
                            pass

                        file_entry += "\n"

                        # Check if adding this complete file entry would exceed the limit
                        test_message = fmsg + file_entry
                        test_full_message = test_message.encode() + msg.encode()

                        # Check if adding this file would exceed the limit
                        if len(test_full_message) > 4000:
                            # If we have at least 10 files, we can always split here
                            if files_in_current_message >= 10:
                                # Don't add this file to current message, it will start the next message
                                break
                            # If we have 8 or 9 files and adding this file would cause truncation,
                            # split here to prevent truncation (even if we don't reach exactly 10 files)
                            if files_in_current_message >= 8:
                                # Don't add this file to current message, it will start the next message
                                # This prevents truncation while still trying to get close to 10 files
                                break
                            # If we have less than 8 files, include this file even if it exceeds the limit
                            # to try to get closer to the 10 file minimum

                        # Add the complete file entry to the message
                        fmsg += file_entry
                        files_in_current_message += 1
                        file_index += 1

                        # If we've processed all files, break
                        if file_index >= total_files:
                            break

                    # Store this message part
                    if fmsg:
                        message_parts.append((fmsg, start_index + 1, file_index))

                # Send all message parts
                for part_index, (fmsg, start_file_num, end_file_num) in enumerate(
                    message_parts
                ):
                    # Add part indicator if there are multiple parts
                    part_msg = msg
                    if len(message_parts) > 1:
                        part_msg = msg.replace(
                            "</blockquote>\n\n",
                            f"\n<b>Part {part_index + 1}/{len(message_parts)}</b> (Files {start_file_num}-{end_file_num})</blockquote>\n\n",
                        )

                    # Send this message part
                    await self._send_message_part(part_msg, fmsg)

                    # Add delay between parts
                    if part_index < len(message_parts) - 1:
                        await sleep(1)

        else:
            # Check if this is a YouTube upload result
            if isinstance(link, dict) and "video_url" in link:
                # YouTube upload result
                youtube_result = link
                if isinstance(youtube_result, list):
                    # Multiple videos uploaded
                    msg += "\n\n<b>Type: </b>YouTube Videos"
                    msg += f"\n<b>Videos Uploaded: </b>{len(youtube_result)}"

                    # Add MediaInfo link if available
                    user_mediainfo_enabled = self.user_dict.get(
                        "MEDIAINFO_ENABLED", None
                    )
                    if user_mediainfo_enabled is None:
                        user_mediainfo_enabled = Config.MEDIAINFO_ENABLED
                    if (
                        user_mediainfo_enabled
                        and hasattr(self, "mediainfo_link")
                        and self.mediainfo_link
                        and self.mediainfo_link.strip()
                    ):
                        msg += f"\n<b>MediaInfo</b> → <a href='https://graph.org/{self.mediainfo_link}'>View</a>"

                    buttons = ButtonMaker()
                    for i, video in enumerate(
                        youtube_result[:5]
                    ):  # Show first 5 videos
                        video_title = video.get("title", f"Video {i + 1}")[:20]
                        buttons.url_button(f"📺 {video_title}", video["video_url"])

                    if len(youtube_result) > 5:
                        msg += f"\n<i>Showing first 5 of {len(youtube_result)} videos</i>"

                    button = buttons.build_menu(1)
                else:
                    # Single video uploaded
                    msg += "\n\n<b>Type: </b>YouTube Video"
                    msg += f"\n<b>Privacy: </b>{youtube_result.get('privacy_status', 'unlisted').title()}"

                    # Add MediaInfo link if available
                    user_mediainfo_enabled = self.user_dict.get(
                        "MEDIAINFO_ENABLED", None
                    )
                    if user_mediainfo_enabled is None:
                        user_mediainfo_enabled = Config.MEDIAINFO_ENABLED
                    if (
                        user_mediainfo_enabled
                        and hasattr(self, "mediainfo_link")
                        and self.mediainfo_link
                        and self.mediainfo_link.strip()
                    ):
                        msg += f"\n<b>MediaInfo</b> → <a href='https://graph.org/{self.mediainfo_link}'>View</a>"

                    buttons = ButtonMaker()
                    buttons.url_button(
                        "📺 Watch on YouTube", youtube_result["video_url"]
                    )
                    button = buttons.build_menu(1)
            elif isinstance(link, dict) and any(
                key in ["GoFile", "StreamTape"] for key in link
            ):
                # DDL upload result
                msg += "\n\n<b>Type: </b>DDL Upload"
                if mime_type == "Folder":
                    msg += f"\n<b>SubFolders: </b>{folders}"
                    msg += f"\n<b>Files: </b>{files}"

                # Add MediaInfo link for DDL uploads if enabled
                user_mediainfo_enabled = self.user_dict.get(
                    "MEDIAINFO_ENABLED", None
                )
                if user_mediainfo_enabled is None:
                    user_mediainfo_enabled = Config.MEDIAINFO_ENABLED
                if (
                    user_mediainfo_enabled
                    and hasattr(self, "mediainfo_link")
                    and self.mediainfo_link
                    and self.mediainfo_link.strip()
                ):
                    msg += f"\n<b>MediaInfo</b> → <a href='https://graph.org/{self.mediainfo_link}'>View</a>"

                # Create buttons for DDL links
                buttons = ButtonMaker()
                for server_name, server_link in link.items():
                    if server_link:
                        if server_name == "GoFile":
                            buttons.url_button("📁 Gofile Link", server_link)
                        elif server_name == "StreamTape":
                            buttons.url_button("🎬 StreamTape Link", server_link)
                        else:
                            buttons.url_button(f"🔗 {server_name}", server_link)

                # Check if ButtonMaker has any buttons before building
                has_buttons = (
                    len(buttons._button) > 0
                    or len(buttons._header_button) > 0
                    or len(buttons._footer_button) > 0
                    or len(buttons._page_button) > 0
                )
                button = buttons.build_menu(1) if has_buttons else None
            else:
                # Regular cloud upload
                msg += f"\n\n<b>Type: </b>{mime_type}"
                if mime_type == "Folder":
                    msg += f"\n<b>SubFolders: </b>{folders}"
                    msg += f"\n<b>Files: </b>{files}"

                # Add MediaInfo link for mirror tasks if enabled
                # Check if MediaInfo is enabled for this user
                user_mediainfo_enabled = self.user_dict.get(
                    "MEDIAINFO_ENABLED", None
                )
                if user_mediainfo_enabled is None:
                    user_mediainfo_enabled = (
                        Config.MEDIAINFO_ENABLED
                    )  # Use the pre-generated MediaInfo link if available and valid
                if (
                    user_mediainfo_enabled
                    and hasattr(self, "mediainfo_link")
                    and self.mediainfo_link
                    and self.mediainfo_link.strip()
                ):
                    # Support all media types including archives, documents, images, etc.
                    msg += f"\n<b>MediaInfo</b> → <a href='https://graph.org/{self.mediainfo_link}'>View</a>"
                    # Log that MediaInfo link was successfully added to the message
                elif user_mediainfo_enabled and hasattr(self, "mediainfo_link"):
                    # MediaInfo was attempted but failed or returned empty
                    pass
                if link or (
                    rclone_path and Config.RCLONE_SERVE_URL and not self.private_link
                ):
                    buttons = ButtonMaker()
                    if link and Config.SHOW_CLOUD_LINK:
                        buttons.url_button("☁️ Cloud Link", link)
                    else:
                        msg += f"\n\nPath: <code>{rclone_path}</code>"
                    if (
                        rclone_path
                        and Config.RCLONE_SERVE_URL
                        and not self.private_link
                    ):
                        remote, rpath = rclone_path.split(":", 1)
                        url_path = rutils.quote(f"{rpath}")
                        share_url = f"{Config.RCLONE_SERVE_URL}/{remote}/{url_path}"
                        if mime_type == "Folder":
                            share_url += "/"
                        buttons.url_button("🔗 Rclone Link", share_url)
                    if not rclone_path and dir_id:
                        INDEX_URL = ""
                        if self.private_link:
                            INDEX_URL = self.user_dict.get("INDEX_URL", "") or ""
                        elif Config.INDEX_URL:
                            INDEX_URL = Config.INDEX_URL
                        if INDEX_URL:
                            share_url = f"{INDEX_URL}findpath?id={dir_id}"
                            buttons.url_button("⚡ Index Link", share_url)
                            if mime_type.startswith(("image", "video", "audio")):
                                share_urls = (
                                    f"{INDEX_URL}findpath?id={dir_id}&view=true"
                                )
                                buttons.url_button("🌐 View Link", share_urls)
                    button = buttons.build_menu(2)
                else:
                    msg += f"\n\nPath: <code>{rclone_path}</code>"
                    button = None
            msg += f"\n\n<b>cc: </b>{self.tag}</blockquote>"

            # Check if user specified a destination with -up flag
            # Only treat as chat destination if it's not a cloud upload destination
            def is_youtube_destination(dest):
                return dest == "yt" or dest.startswith("yt:")

            def is_mega_destination(dest):
                return dest == "mg" or dest.startswith("mg:")

            from bot.helper.common import is_ddl_destination

            if (
                self.up_dest
                and not is_gdrive_id(self.up_dest)
                and not is_rclone_path(self.up_dest)
                and not is_youtube_destination(self.up_dest)
                and not is_mega_destination(self.up_dest)
                and not is_ddl_destination(self.up_dest)
            ):
                # If user specified a destination with -up flag, it takes precedence
                try:
                    # Send to the specified destination
                    await send_message(int(self.up_dest), msg, button)
                    # Also send to user's PM if it's not the same as the specified destination
                    if int(self.up_dest) != self.user_id:
                        await send_message(self.user_id, msg, button)
                except Exception as e:
                    LOGGER.error(
                        f"Failed to send mirror log to specified destination {self.up_dest}: {e}"
                    )
                    # Fallback to user's PM
                    await send_message(self.user_id, msg, button)
            else:
                # No specific destination was specified or it's a cloud destination
                # Determine mirror log destinations based on requirements
                mirror_destinations = []

                # Only add user's PM for file details, not for task completion messages
                # We'll send the task completion message only to groups/supergroups
                mirror_destinations.append(self.user_id)

                # Check if user has set their own dump
                user_dump = self.user_dict.get("USER_DUMP")

                # Case 1: If user set their own dump and owner has set log chat id
                if user_dump and Config.LOG_CHAT_ID:
                    # Send to user dump, owner log chat id, and bot PM
                    mirror_destinations.append(int(user_dump))
                    mirror_destinations.append(int(Config.LOG_CHAT_ID))

                # Case 2: If user set their own dump and owner didn't set log chat id
                elif user_dump and not Config.LOG_CHAT_ID:
                    # Send to user dump and bot PM
                    mirror_destinations.append(int(user_dump))

                # Case 3: If user didn't set their own dump and owner set log chat id
                elif not user_dump and Config.LOG_CHAT_ID:
                    # Send to owner log chat id and bot PM
                    mirror_destinations.append(int(Config.LOG_CHAT_ID))

                # Remove duplicates while preserving order
                seen = set()
                mirror_destinations = [
                    x for x in mirror_destinations if not (x in seen or seen.add(x))
                ]

                # Send to all destinations including user's PM
                for dest in mirror_destinations:
                    try:
                        await send_message(dest, msg, button)
                    except Exception as e:
                        LOGGER.error(
                            f"Failed to send mirror log to destination {dest}: {e}"
                        )

            # Send completion message only to the original chat if it's a group or supergroup
            # Add "Checkout Inbox" button for group/supergroup chats
            button = None
            if (
                not self.is_leech  # Only for mirror operations
                and self.message.chat.type != "private"
                and self.message.chat.id != self.user_id
            ):
                # Only send completion message to the original chat if it's a group or supergroup
                # and not the user's PM
                buttons = ButtonMaker()
                buttons.url_button("Checkout Inbox", f"https://t.me/{TgClient.NAME}")
                button = buttons.build_menu(1)

                await send_message(self.message, done_msg, button)

        # For leech operations, send simple completion message to groups/supergroups
        if self.is_leech and (
            self.message.chat.type != "private"
            and self.message.chat.id != self.user_id
        ):
            # Send simple completion message to groups/supergroups for leech operations
            buttons = ButtonMaker()
            buttons.url_button("Checkout Inbox", f"https://t.me/{TgClient.NAME}")
            button = buttons.build_menu(1)

            await send_message(self.message, done_msg, button)
        # We don't need to delete command messages here
        # They are already being deleted in the on_download_complete method

        if self.seed:
            await clean_target(self.up_dir)
            async with queue_dict_lock:
                if self.mid in non_queued_up:
                    non_queued_up.remove(self.mid)
            await start_from_queued()
            return

        # Add a delay before cleaning up to ensure all processes are complete
        await sleep(3)

        # Now clean up the download directory
        await clean_download(self.dir)
        async with task_dict_lock:
            if self.mid in task_dict:
                del task_dict[self.mid]
            count = len(task_dict)
        if count == 0:
            await self.clean()
        else:
            await update_status_message(self.message.chat.id)

        async with queue_dict_lock:
            if self.mid in non_queued_up:
                non_queued_up.remove(self.mid)

        await start_from_queued()

    async def on_download_error(self, error, button=None):
        async with task_dict_lock:
            if self.mid in task_dict:
                del task_dict[self.mid]
            count = len(task_dict)
        await self.remove_from_same_dir()

        # Check if this is a leech task with dump chat messages
        if (
            self.is_leech
            and hasattr(self, "telegram_uploader")
            and hasattr(self.telegram_uploader, "dump_chat_msgs")
        ):
            # Keep track of command messages in dump chats
            dump_chat_msgs = self.telegram_uploader.dump_chat_msgs

            # Delete command messages in dump chats if task is cancelled by user
            if "cancelled by user" in str(error).lower():
                for chat_id, msg in dump_chat_msgs.items():
                    try:
                        await delete_message(msg)
                    except Exception as e:
                        LOGGER.error(
                            f"Failed to delete command message in dump chat {chat_id}: {e}"
                        )
            else:
                pass
        else:
            # For non-leech tasks or tasks without dump chat messages, delete the original command message

            await delete_links(self.message)

        # Check if error is already a message object (from limit_checker)
        if isinstance(error, tuple) and len(error) == 2:
            # This is a tuple from limit_checker with (message_object, error_message)
            # The message has already been sent with the tag, so we don't need to send it again
            error_msg = error[0]  # Use the message that was already sent
        else:
            # Send and auto-delete error message
            # Make sure to include the user tag
            error_str = escape(str(error))
            if "⚠️" in error_str and "limit" in error_str.lower():
                # This is a limit error, make sure to tag the user
                msg = f"{self.tag} ⚠️ Download Error: {error_str}"
            else:
                msg = f"{self.tag} Download: {error_str}"

            error_msg = await send_message(self.message, msg, button)
            create_task(
                auto_delete_message(error_msg, time=300),
            )  # noqa: RUF006, RUF100

        if count == 0:
            await self.clean()
        else:
            await update_status_message(self.message.chat.id)

        if (
            self.is_super_chat
            and Config.INCOMPLETE_TASK_NOTIFIER
            and Config.DATABASE_URL
        ):
            await database.rm_complete_task(self.message.link)

        async with queue_dict_lock:
            if self.mid in queued_dl:
                queued_dl[self.mid].set()
                del queued_dl[self.mid]
            if self.mid in queued_up:
                queued_up[self.mid].set()
                del queued_up[self.mid]
            if self.mid in non_queued_dl:
                non_queued_dl.remove(self.mid)
            if self.mid in non_queued_up:
                non_queued_up.remove(self.mid)

        await start_from_queued()

        # Add a delay before cleaning up to ensure all processes are complete
        await sleep(5)

        # Now clean up the download directory
        await clean_download(self.dir)
        if self.up_dir:
            await clean_download(self.up_dir)
        if self.thumb and await aiopath.exists(self.thumb):
            await remove(self.thumb)

    async def on_upload_error(self, error):
        async with task_dict_lock:
            if self.mid in task_dict:
                del task_dict[self.mid]
            count = len(task_dict)

        # Check if this is a leech task with dump chat messages
        if (
            self.is_leech
            and hasattr(self, "telegram_uploader")
            and hasattr(self.telegram_uploader, "dump_chat_msgs")
        ):
            # Keep track of command messages in dump chats
            dump_chat_msgs = self.telegram_uploader.dump_chat_msgs

            # Delete command messages in dump chats if task is cancelled by user
            if "stopped" in str(error).lower() or "cancelled" in str(error).lower():
                for chat_id, msg in dump_chat_msgs.items():
                    try:
                        await delete_message(msg)
                    except Exception as e:
                        LOGGER.error(
                            f"Failed to delete command message in dump chat {chat_id}: {e}"
                        )
            else:
                pass
        else:
            # For non-leech tasks or tasks without dump chat messages, delete the original command message

            await delete_links(self.message)

        # Check if error is already a message object (from limit_checker)
        if isinstance(error, tuple) and len(error) == 2:
            # This is a tuple from limit_checker with (message_object, error_message)
            # The message has already been sent with the tag, so we don't need to send it again
            x = error[0]  # Use the message that was already sent
        else:
            # Send and auto-delete error message with the user tag
            x = await send_message(self.message, f"{self.tag} {escape(str(error))}")
            create_task(auto_delete_message(x, time=300))  # noqa: RUF006, RUF100
        if count == 0:
            await self.clean()
        else:
            await update_status_message(self.message.chat.id)

        # Check if is_super_chat is a valid boolean attribute
        is_super_chat = (
            hasattr(self, "is_super_chat")
            and not callable(getattr(self, "is_super_chat", None))
            and self.is_super_chat
        )

        if is_super_chat and Config.INCOMPLETE_TASK_NOTIFIER and Config.DATABASE_URL:
            await database.rm_complete_task(self.message.link)

        async with queue_dict_lock:
            if self.mid in queued_dl:
                queued_dl[self.mid].set()
                del queued_dl[self.mid]
            if self.mid in queued_up:
                queued_up[self.mid].set()
                del queued_up[self.mid]
            if self.mid in non_queued_dl:
                non_queued_dl.remove(self.mid)
            if self.mid in non_queued_up:
                non_queued_up.remove(self.mid)

        await start_from_queued()

        # Add a delay before cleaning up to ensure all processes are complete
        await sleep(5)

        # Now clean up the download directory
        await clean_download(self.dir)
        if self.up_dir:
            await clean_download(self.up_dir)
        if self.thumb and await aiopath.exists(self.thumb):
            await remove(self.thumb)

    async def proceed_add(self, up_path, gid):
        """Process add functionality for media files."""
        from bot.helper.aeon_utils.command_gen import get_add_cmd

        LOGGER.info(f"Starting add processing for: {up_path}")

        if self.is_cancelled:
            return up_path

        # Check if any add functionality is enabled
        if not (
            self.add_video_enabled
            or self.add_audio_enabled
            or self.add_subtitle_enabled
            or self.add_attachment_enabled
        ):
            LOGGER.info("No add functionality enabled, skipping add processing")
            return up_path

        try:
            # Prepare multi-files list if available
            multi_files = None
            if hasattr(self, "multi_files") and self.multi_files:
                multi_files = self.multi_files

            # Generate add command
            cmd, temp_file = await get_add_cmd(
                file_path=up_path,
                add_video=self.add_video_enabled,
                add_audio=self.add_audio_enabled,
                add_subtitle=self.add_subtitle_enabled,
                add_attachment=self.add_attachment_enabled,
                video_index=self.add_video_index,
                audio_index=self.add_audio_index,
                subtitle_index=self.add_subtitle_index,
                attachment_index=self.add_attachment_index,
                video_codec=self.add_video_codec,
                audio_codec=self.add_audio_codec,
                subtitle_codec=self.add_subtitle_codec,
                video_quality=self.add_video_quality,
                video_preset=self.add_video_preset,
                video_bitrate=self.add_video_bitrate,
                video_resolution=self.add_video_resolution,
                video_fps=self.add_video_fps,
                audio_bitrate=self.add_audio_bitrate,
                audio_channels=self.add_audio_channels,
                audio_sampling=self.add_audio_sampling,
                audio_volume=self.add_audio_volume,
                subtitle_language=self.add_subtitle_language,
                subtitle_encoding=self.add_subtitle_encoding,
                subtitle_font=self.add_subtitle_font,
                subtitle_font_size=self.add_subtitle_font_size,
                subtitle_hardsub_enabled=self.add_subtitle_hardsub_enabled,
                attachment_mimetype=self.add_attachment_mimetype,
                delete_original=self.add_delete_original,
                preserve_tracks=self.add_preserve_tracks,
                replace_tracks=self.add_replace_tracks,
                multi_files=multi_files,
            )

            if not cmd:
                LOGGER.warning("Failed to generate add command")
                return up_path

            LOGGER.info(f"Generated add command: {' '.join(cmd[:10])}...")

            # Process the command using FFMpeg
            from bot.helper.ext_utils.media_utils import FFMpeg

            processor = FFMpeg(self)
            result = await processor.ffmpeg_cmds(cmd, up_path)

            if result and isinstance(result, list) and result:
                # Return the first processed file
                processed_file = result[0]
                LOGGER.info(f"Add processing completed: {processed_file}")
                return processed_file

            LOGGER.error("Add processing failed")
            return up_path

        except Exception as e:
            LOGGER.error(f"Error during add processing: {e}")
            return up_path
