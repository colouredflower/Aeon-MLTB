from asyncio import Event, create_task, wait_for
from functools import partial
from os import path as ospath
from time import time

from httpx import AsyncClient
from pyrogram.filters import regex, user
from pyrogram.handlers import CallbackQueryHandler
from yt_dlp import YoutubeDL

from bot import DOWNLOAD_DIR, LOGGER, bot_loop, task_dict_lock
from bot.core.config_manager import Config
from bot.helper.aeon_utils.access_check import error_check
from bot.helper.ext_utils.bot_utils import (
    COMMAND_USAGE,
    arg_parser,
    new_task,
    sync_to_async,
)
from bot.helper.ext_utils.links_utils import is_url
from bot.helper.ext_utils.status_utils import (
    get_readable_file_size,
    get_readable_time,
)
from bot.helper.listeners.task_listener import TaskListener
from bot.helper.mirror_leech_utils.download_utils.yt_dlp_download import (
    YoutubeDLHelper,
)
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.telegram_helper.message_utils import (
    auto_delete_message,
    delete_links,
    delete_message,
    edit_message,
    send_message,
)


@new_task
async def select_format(_, query, obj):
    data = query.data.split()
    await query.answer()

    if data[1] == "dict":
        b_name = data[2]
        await obj.qual_subbuttons(b_name)
    elif data[1] == "mp3":
        await obj.mp3_subbuttons()
    elif data[1] == "audio":
        await obj.audio_format()
    elif data[1] == "info":
        # For section headers, show a helpful message
        await query.answer(
            "This is a section header. Please select a format below.",
            show_alert=True,
        )
    elif data[1] == "section":
        # Handle section selection
        try:
            section = data[2]
            await obj.show_section(section)
        except Exception as e:
            LOGGER.error(f"Error in section selection: {e}")
            await query.answer(f"Error: {e!s}", show_alert=True)
    elif data[1] == "aq":
        # Handle audio quality format selection
        await obj.audio_quality(data[2])
    elif data[1] == "back":
        await obj.back_to_main()
    elif data[1] == "cancel":
        # First send cancellation message
        cancel_msg = await send_message(
            obj.listener.message,
            f"{obj.listener.tag} Task has been cancelled!",
        )

        # Delete the selection menu
        await delete_message(obj._reply_to)

        # Delete the original command
        await delete_message(obj.listener.message)

        # Create background task for auto-deletion
        create_task(  # noqa: RUF006
            auto_delete_message(cancel_msg, time=300),
        )  # 5 minutes auto-delete

        obj.qual = None
        obj.listener.is_cancelled = True
        obj.event.set()
    else:
        if data[1] == "sub":
            obj.qual = obj.formats[data[2]][data[3]][1]
        elif "|" in data[1]:
            obj.qual = obj.formats[data[1]]
        else:
            obj.qual = data[1]
        obj.event.set()


class YtSelection:
    def __init__(self, listener):
        self.listener = listener
        self._is_m4a = False
        self._reply_to = None
        self._time = time()
        self._timeout = 120
        self._is_playlist = False
        self._main_buttons = None
        self.event = Event()
        self.formats = {}
        self.qual = None

    async def _event_handler(self):
        pfunc = partial(select_format, obj=self)
        handler = self.listener.client.add_handler(
            CallbackQueryHandler(
                pfunc,
                filters=regex("^ytq") & user(self.listener.user_id),
            ),
            group=-1,
        )
        try:
            await wait_for(self.event.wait(), timeout=self._timeout)
        except Exception:
            # Delete both original command and its replied message
            await delete_links(self.listener.message)

            # Send new timeout message instead of editing
            timeout_msg = await send_message(
                self.listener.message,
                f"{self.listener.tag} Timed Out. Task has been cancelled!",
            )

            # Delete the selection menu
            await delete_message(self._reply_to)

            # Create background task to delete timeout message after 5 minutes
            create_task(  # noqa: RUF006
                auto_delete_message(timeout_msg, time=300),
            )  # 5 minutes auto-delete

            self.qual = None
            self.listener.is_cancelled = True
            self.event.set()
        finally:
            self.listener.client.remove_handler(*handler)

    async def show_section(self, section):
        buttons = ButtonMaker()

        if self._is_playlist:
            # For playlists, show predefined formats
            if section == "sd":
                # SD formats (144p, 240p, 360p, 480p) in ascending order
                for i in ["144", "240", "360", "480"]:
                    # MP4 format with audio
                    b_data = f"{i}|mp4"
                    buttons.data_button(f"{i}p MP4", f"ytq {b_data}")

                    # WebM format with audio
                    b_data = f"{i}|webm"
                    buttons.data_button(f"{i}p WebM", f"ytq {b_data}")

            elif section == "hd":
                # HD formats (720p, 1080p) in ascending order
                for i in ["720", "1080"]:
                    # MP4 format with audio
                    b_data = f"{i}|mp4"
                    buttons.data_button(f"{i}p MP4", f"ytq {b_data}")

                    # WebM format with audio
                    b_data = f"{i}|webm"
                    buttons.data_button(f"{i}p WebM", f"ytq {b_data}")

                    # AV1 format with audio
                    b_data = f"{i}|av1"
                    buttons.data_button(f"{i}p AV1", f"ytq {b_data}")

            elif section == "4k":
                # 4K formats (1440p, 2160p) in ascending order
                for i in ["1440", "2160"]:
                    # MP4 format with audio
                    b_data = f"{i}|mp4"
                    buttons.data_button(f"{i}p MP4", f"ytq {b_data}")

                    # WebM format with audio
                    b_data = f"{i}|webm"
                    buttons.data_button(f"{i}p WebM", f"ytq {b_data}")

                    # AV1 format with audio
                    b_data = f"{i}|av1"
                    buttons.data_button(f"{i}p AV1", f"ytq {b_data}")

        # For single videos, show available formats from the extracted info
        elif section in ["sd", "hd", "4k"]:
            # Define resolution ranges for each section
            if section == "sd":
                # SD: below 720p
                def res_range(r):
                    return r < 720
            elif section == "hd":
                # HD: 720p to 1440p (exclusive)
                def res_range(r):
                    return 720 <= r < 1440
            else:  # 4k
                # 4K: 1440p and above
                def res_range(r):
                    return r >= 1440

            # Get all resolutions in this range
            matching_resolutions = []
            for r in self.formats:
                # Check if the format name contains 'p' and has a number before it
                if "p" in r:
                    try:
                        # Try to extract the resolution number
                        res_num = int(r.split("p")[0])
                        # Check if it's in the desired range
                        if res_range(res_num):
                            matching_resolutions.append(r)
                    except (ValueError, IndexError):
                        # Skip formats that don't have a valid resolution number
                        continue

            # Sort resolutions in ascending order
            def get_resolution(format_name):
                try:
                    if "p" in format_name:
                        return int(format_name.split("p")[0])
                    return 0
                except (ValueError, IndexError):
                    return 0

            # Check if we found any matching resolutions
            if not matching_resolutions:
                # No formats in this resolution range
                buttons.data_button(
                    f"No {section.upper()} formats available", "ytq info"
                )
            else:
                # Add formats in ascending order
                for b_name in sorted(matching_resolutions, key=get_resolution):
                    try:
                        tbr_dict = self.formats[b_name]
                        if len(tbr_dict) == 1:
                            tbr, v_list = next(iter(tbr_dict.items()))
                            size_str = get_readable_file_size(v_list[0])
                            # Highlight AV1 formats
                            if "av1" in b_name.lower():
                                buttonName = f"🔸 {b_name} ({size_str})"
                            else:
                                buttonName = f"{b_name} ({size_str})"
                            buttons.data_button(
                                buttonName, f"ytq sub {b_name} {tbr}"
                            )
                        else:
                            buttons.data_button(b_name, f"ytq dict {b_name}")
                    except Exception as e:
                        LOGGER.error(f"Error adding format button {b_name}: {e}")
                        continue

        # Audio options section is the same for both playlist and single videos
        if section == "audio":
            # Audio options
            buttons.data_button("MP3 Audio", "ytq mp3")
            buttons.data_button("Other Audio Formats", "ytq audio")
            buttons.data_button("Best Audio", "ytq bestaudio")

        # Quick options section is the same for both playlist and single videos
        elif section == "quick":
            # Quick options
            buttons.data_button("Best Video", "ytq bestvideo+bestaudio")
            buttons.data_button("Best Audio", "ytq bestaudio")

        # Add back button
        buttons.data_button("Back", "ytq back", "footer")
        buttons.data_button("Cancel", "ytq cancel", "footer")

        subbuttons = buttons.build_menu(2)
        msg = f"Choose {section.upper()} Format:\nTimeout: {get_readable_time(self._timeout - (time() - self._time))}"
        await edit_message(self._reply_to, msg, subbuttons)

    async def get_quality(self, result):
        buttons = ButtonMaker()
        if "entries" in result:
            self._is_playlist = True

            # Store all formats for later use
            # SD formats
            for i in ["144", "240", "360", "480"]:
                # MP4 format with audio
                video_format = (
                    f"bv*[height<=?{i}][ext=mp4]+ba[ext=m4a]/b[height<=?{i}]"
                )
                b_data = f"{i}|mp4"
                self.formats[b_data] = video_format

                # WebM format with audio
                video_format = f"bv*[height<=?{i}][ext=webm]+ba/b[height<=?{i}]"
                b_data = f"{i}|webm"
                self.formats[b_data] = video_format

            # HD formats
            for i in ["720", "1080"]:
                # MP4 format with audio
                video_format = (
                    f"bv*[height<=?{i}][ext=mp4]+ba[ext=m4a]/b[height<=?{i}]"
                )
                b_data = f"{i}|mp4"
                self.formats[b_data] = video_format

                # WebM format with audio
                video_format = f"bv*[height<=?{i}][ext=webm]+ba/b[height<=?{i}]"
                b_data = f"{i}|webm"
                self.formats[b_data] = video_format

                # AV1 format with audio
                video_format = f"bv*[height<=?{i}][vcodec*=av01]+ba/b[height<=?{i}]"
                b_data = f"{i}|av1"
                self.formats[b_data] = video_format

            # 4K formats
            for i in ["1440", "2160"]:
                # MP4 format with audio
                video_format = (
                    f"bv*[height<=?{i}][ext=mp4]+ba[ext=m4a]/b[height<=?{i}]"
                )
                b_data = f"{i}|mp4"
                self.formats[b_data] = video_format

                # WebM format with audio
                video_format = f"bv*[height<=?{i}][ext=webm]+ba/b[height<=?{i}]"
                b_data = f"{i}|webm"
                self.formats[b_data] = video_format

                # AV1 format with audio
                video_format = f"bv*[height<=?{i}][vcodec*=av01]+ba/b[height<=?{i}]"
                b_data = f"{i}|av1"
                self.formats[b_data] = video_format

            # Add all video formats directly to the main menu in ascending order
            # SD formats (144p, 240p, 360p, 480p)
            for i in ["144", "240", "360", "480"]:
                # MP4 format with audio
                b_data = f"{i}|mp4"
                buttons.data_button(f"{i}p MP4", f"ytq {b_data}")

                # WebM format with audio
                b_data = f"{i}|webm"
                buttons.data_button(f"{i}p WebM", f"ytq {b_data}")

            # HD formats (720p, 1080p)
            for i in ["720", "1080"]:
                # MP4 format with audio
                b_data = f"{i}|mp4"
                buttons.data_button(f"{i}p MP4", f"ytq {b_data}")

                # WebM format with audio
                b_data = f"{i}|webm"
                buttons.data_button(f"{i}p WebM", f"ytq {b_data}")

                # AV1 format with audio
                b_data = f"{i}|av1"
                buttons.data_button(f"{i}p AV1", f"ytq {b_data}")

            # 4K formats (1440p, 2160p)
            for i in ["1440", "2160"]:
                # MP4 format with audio
                b_data = f"{i}|mp4"
                buttons.data_button(f"{i}p MP4", f"ytq {b_data}")

                # WebM format with audio
                b_data = f"{i}|webm"
                buttons.data_button(f"{i}p WebM", f"ytq {b_data}")

                # AV1 format with audio
                b_data = f"{i}|av1"
                buttons.data_button(f"{i}p AV1", f"ytq {b_data}")

            # Add Best Video option after all video formats
            buttons.data_button("🔹 BEST VIDEO 🔹", "ytq bestvideo+bestaudio")

            # Best Audio and Audios buttons
            buttons.data_button("🔹 BEST AUDIO 🔹", "ytq bestaudio")
            buttons.data_button("🔹 AUDIOS 🔹", "ytq section audio")
            buttons.data_button("Cancel", "ytq cancel", "footer")

            self._main_buttons = buttons.build_menu(2)
            msg = f"Choose Playlist Videos Quality:\nTimeout: {get_readable_time(self._timeout - (time() - self._time))}"
        else:
            format_dict = result.get("formats")
            if format_dict is not None:
                # Group formats by codec for better organization
                codec_groups = {}

                for item in format_dict:
                    if item.get("tbr"):
                        format_id = item["format_id"]

                        if item.get("filesize"):
                            size = item["filesize"]
                        elif item.get("filesize_approx"):
                            size = item["filesize_approx"]
                        else:
                            size = 0

                        # Handle audio formats
                        if item.get("video_ext") == "none" and (
                            item.get("resolution") == "audio only"
                            or item.get("acodec") != "none"
                        ):
                            if item.get("audio_ext") == "m4a":
                                self._is_m4a = True
                            b_name = (
                                f"{item.get('acodec') or format_id}-{item['ext']}"
                            )
                            v_format = format_id

                            # Add to audio group
                            codec_group = "audio"

                        # Handle video formats
                        elif item.get("height"):
                            height = item["height"]
                            ext = item["ext"]
                            fps = item["fps"] if item.get("fps") else ""

                            # Identify codec for grouping
                            vcodec = item.get("vcodec", "")
                            if "av01" in vcodec:
                                codec_group = "av1"
                            elif "avc" in vcodec or "h264" in vcodec:
                                codec_group = "h264"
                            elif "vp9" in vcodec:
                                codec_group = "vp9"
                            else:
                                codec_group = ext

                            b_name = f"{height}p{fps}-{codec_group}"
                            ba_ext = (
                                "[ext=m4a]" if self._is_m4a and ext == "mp4" else ""
                            )
                            v_format = f"{format_id}+ba{ba_ext}/b[height=?{height}]"
                        else:
                            continue

                        # Store format info
                        self.formats.setdefault(b_name, {})[f"{item['tbr']}"] = [
                            size,
                            v_format,
                        ]

                        # Group by codec for better UI organization
                        codec_groups.setdefault(codec_group, []).append(b_name)

                # Sort formats by resolution (height)
                sorted_formats = []
                for b_name in self.formats:
                    try:
                        # Extract resolution from format name (e.g., "720p-h264" -> 720)
                        if "p" in b_name:
                            resolution = int(b_name.split("p")[0])
                            sorted_formats.append((resolution, b_name))
                    except (ValueError, IndexError):
                        # If we can't extract resolution, add it with resolution 0
                        sorted_formats.append((0, b_name))

                # Sort by resolution (lowest to highest)
                sorted_formats.sort()

                # Add all formats to the main menu
                for _, b_name in sorted_formats:
                    tbr_dict = self.formats[b_name]
                    if len(tbr_dict) == 1:
                        tbr, v_list = next(iter(tbr_dict.items()))
                        size_str = get_readable_file_size(v_list[0])
                        # Highlight AV1 formats
                        if "av1" in b_name.lower():
                            buttonName = f"🔸 {b_name} ({size_str})"
                        else:
                            buttonName = f"{b_name} ({size_str})"
                        buttons.data_button(buttonName, f"ytq sub {b_name} {tbr}")
                    else:
                        buttons.data_button(b_name, f"ytq dict {b_name}")

                # Add Best Video option after all video formats
                buttons.data_button("🔹 BEST VIDEO 🔹", "ytq bestvideo+bestaudio")

            # Best Audio and Audios buttons
            buttons.data_button("🔹 BEST AUDIO 🔹", "ytq bestaudio")
            buttons.data_button("🔹 AUDIOS 🔹", "ytq section audio")
            buttons.data_button("Cancel", "ytq cancel", "footer")

            self._main_buttons = buttons.build_menu(2)
            msg = f"Choose Video Quality:\nTimeout: {get_readable_time(self._timeout - (time() - self._time))}"

        self._reply_to = await send_message(
            self.listener.message,
            msg,
            self._main_buttons,
        )
        await self._event_handler()
        if not self.listener.is_cancelled:
            await delete_message(self._reply_to)
        return self.qual

    async def back_to_main(self):
        # Get the current message text to determine which menu we're in
        current_msg = self._reply_to.text if hasattr(self._reply_to, "text") else ""

        # Check if we're in an audio-related menu
        if "Audio" in current_msg and "Quality" in current_msg:
            # We're in the audio quality menu, go back to audio format selection
            await self.audio_format()
        elif "Audio Format" in current_msg:
            # We're in the audio format menu, go back to audio section
            await self.show_section("audio")
        elif "MP3 Audio" in current_msg:
            # We're in the MP3 quality menu, go back to audio section
            await self.show_section("audio")
        elif "Choose AUDIO Format" in current_msg:
            # We're in the audio section, go back to main menu
            if self._is_playlist:
                msg = f"Choose Playlist Videos Quality:\nTimeout: {get_readable_time(self._timeout - (time() - self._time))}"
            else:
                msg = f"Choose Video Quality:\nTimeout: {get_readable_time(self._timeout - (time() - self._time))}"
            await edit_message(self._reply_to, msg, self._main_buttons)
        else:
            # Default: go back to main menu
            if self._is_playlist:
                msg = f"Choose Playlist Videos Quality:\nTimeout: {get_readable_time(self._timeout - (time() - self._time))}"
            else:
                msg = f"Choose Video Quality:\nTimeout: {get_readable_time(self._timeout - (time() - self._time))}"
            await edit_message(self._reply_to, msg, self._main_buttons)

    async def qual_subbuttons(self, b_name):
        buttons = ButtonMaker()
        tbr_dict = self.formats[b_name]
        for tbr, d_data in tbr_dict.items():
            button_name = f"{tbr}K ({get_readable_file_size(d_data[0])})"
            buttons.data_button(button_name, f"ytq sub {b_name} {tbr}")
        buttons.data_button("Back", "ytq back", "footer")
        buttons.data_button("Cancel", "ytq cancel", "footer")
        subbuttons = buttons.build_menu(2)
        msg = f"Choose Bit rate for <b>{b_name}</b>:\nTimeout: {get_readable_time(self._timeout - (time() - self._time))}"
        await edit_message(self._reply_to, msg, subbuttons)

    async def mp3_subbuttons(self):
        i = "s" if self._is_playlist else ""
        buttons = ButtonMaker()

        # Audio qualities from lowest to highest
        audio_qualities = [64, 128, 192, 256, 320]

        # Add quality description for better understanding
        quality_desc = {
            64: "Low Quality (Smallest Size)",
            128: "Standard Quality",
            192: "Good Quality",
            256: "High Quality",
            320: "Best Quality (Largest Size)",
        }

        for q in audio_qualities:
            audio_format = f"ba/b-mp3-{q}"
            buttons.data_button(f"{q}K - {quality_desc[q]}", f"ytq {audio_format}")

        buttons.data_button("Back", "ytq back", "footer")
        buttons.data_button("Cancel", "ytq cancel", "footer")

        subbuttons = buttons.build_menu(
            1
        )  # One button per row for better readability
        msg = f"Choose MP3 Audio{i} Bitrate (Lowest to Highest Quality):\nTimeout: {get_readable_time(self._timeout - (time() - self._time))}"
        await edit_message(self._reply_to, msg, subbuttons)

    async def audio_format(self):
        i = "s" if self._is_playlist else ""
        buttons = ButtonMaker()

        # Define audio formats with quality information (ordered from lowest to highest quality)
        audio_formats = [
            # Format, Description, Quality Level (1-10, higher is better)
            ("aac", "AAC (Basic Quality)", 3),
            ("mp3", "MP3 (Common Format)", 4),
            ("m4a", "M4A (AAC in M4A)", 5),
            ("vorbis", "OGG (Good Compression)", 6),
            ("opus", "OPUS (Best Compression)", 7),
            ("alac", "ALAC (Apple Lossless)", 9),
            ("flac", "FLAC (Lossless)", 9),
            ("wav", "WAV (Uncompressed)", 10),
        ]

        # Sort by quality level (lowest to highest)
        audio_formats.sort(key=lambda x: x[2])

        # Add audio formats to the menu
        for frmt, desc, _ in audio_formats:
            audio_format = f"ba/b-{frmt}-"
            buttons.data_button(f"{frmt.upper()} - {desc}", f"ytq aq {audio_format}")

        # Add back and cancel buttons
        buttons.data_button("Back", "ytq back", "footer")
        buttons.data_button("Cancel", "ytq cancel", "footer")

        subbuttons = buttons.build_menu(
            1
        )  # Use 1 button per row for better readability
        msg = f"Choose Audio{i} Format (Lowest to Highest Quality):\nTimeout: {get_readable_time(self._timeout - (time() - self._time))}"
        await edit_message(self._reply_to, msg, subbuttons)

    async def audio_quality(self, format):
        i = "s" if self._is_playlist else ""
        buttons = ButtonMaker()

        # In yt-dlp, 0 is best and 10 is worst, but we want to display from lowest to highest quality
        # So we'll reverse the order for display (10 to 0)
        quality_levels = list(range(11))
        quality_levels.reverse()  # Now 10 is first (lowest quality) and 0 is last (highest quality)

        # Add quality descriptions
        quality_desc = {
            10: "Lowest Quality (Smallest Size)",
            8: "Very Low Quality",
            6: "Low Quality",
            4: "Medium Quality",
            2: "High Quality",
            0: "Best Quality (Largest Size)",
        }

        for qual in quality_levels:
            audio_format = f"{format}{qual}"
            # Add description for certain quality levels
            if qual in quality_desc:
                button_text = f"{qual} - {quality_desc[qual]}"
            else:
                button_text = str(qual)

            buttons.data_button(button_text, f"ytq {audio_format}")

        buttons.data_button("Back", "ytq back", "footer")
        buttons.data_button("Cancel", "ytq cancel", "footer")

        subbuttons = buttons.build_menu(2)
        msg = f"Choose Audio{i} Quality (Lowest to Highest):\nNote: 10 is lowest quality, 0 is highest quality\nTimeout: {get_readable_time(self._timeout - (time() - self._time))}"
        await edit_message(self._reply_to, msg, subbuttons)


def extract_info(link, options):
    with YoutubeDL(options) as ydl:
        result = ydl.extract_info(link, download=False)
        if result is None:
            raise ValueError("Info result is None")
        return result


async def _mdisk(link, name):
    key = link.split("/")[-1]
    async with AsyncClient(verify=False) as client:
        resp = await client.get(
            f"https://diskuploader.entertainvideo.com/v1/file/cdnurl?param={key}",
        )
    if resp.status_code == 200:
        resp_json = resp.json()
        link = resp_json["source"]
        if not name:
            name = resp_json["filename"]
    return name, link


class YtDlp(TaskListener):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        client,
        message,
        _=None,  # Placeholder for compatibility with Mirror class
        is_leech=False,
        # These parameters are unused but required for compatibility with Mirror class
        **kwargs,
    ):
        # Extract parameters from kwargs with defaults
        same_dir = kwargs.get("same_dir", {})
        bulk = kwargs.get("bulk", [])
        multi_tag = kwargs.get("multi_tag")
        options = kwargs.get("options", "")
        if same_dir is None:
            same_dir = {}
        if bulk is None:
            bulk = []
        self.message = message
        self.client = client
        self.multi_tag = multi_tag
        self.options = options
        self.same_dir = same_dir
        self.bulk = bulk
        super().__init__()
        self.is_ytdlp = True
        self.is_leech = is_leech

    async def new_event(self):
        text = self.message.text.split("\n")
        input_list = text[0].split(" ")
        qual = ""
        error_msg, error_button = await error_check(self.message)
        if error_msg:
            await delete_links(self.message)
            error = await send_message(self.message, error_msg, error_button)
            create_task(auto_delete_message(error, time=300))  # noqa: RUF006
            return

        args = {
            "-doc": False,
            "-med": False,
            "-s": False,
            "-b": False,
            "-z": False,
            "-sv": False,
            "-ss": False,
            "-f": False,
            "-fd": False,
            "-fu": False,
            "-hl": False,
            "-bt": False,
            "-ut": False,
            "-merge-video": False,
            "-merge-audio": False,
            "-merge-subtitle": False,
            "-merge-all": False,
            "-merge-image": False,
            "-merge-pdf": False,
            "-watermark": False,
            "-iwm": False,
            "-extract": False,
            "-extract-video": False,
            "-extract-audio": False,
            "-extract-subtitle": False,
            "-extract-attachment": False,
            "-add": False,
            "-add-video": False,
            "-add-audio": False,
            "-add-subtitle": False,
            "-add-attachment": False,
            "-trim": False,
            "-compress": False,
            "-comp-video": False,
            "-comp-audio": False,
            "-comp-image": False,
            "-comp-document": False,
            "-comp-subtitle": False,
            "-comp-archive": False,
            "-i": 0,
            "-sp": 0,
            "link": "",
            "-m": "",
            "-opt": {},
            "-n": "",
            "-up": "",
            "-rcf": "",
            "-t": "",
            "-ca": "",
            "-cv": "",
            "-cs": "",
            "-cd": "",
            "-cr": "",
            "-ns": "",
            "-md": "",
            "-metadata-title": "",
            "-metadata-author": "",
            "-metadata-comment": "",
            "-metadata-all": "",
            "-metadata-video-title": "",
            "-metadata-video-author": "",
            "-metadata-video-comment": "",
            "-metadata-audio-title": "",
            "-metadata-audio-author": "",
            "-metadata-audio-comment": "",
            "-metadata-subtitle-title": "",
            "-metadata-subtitle-author": "",
            "-metadata-subtitle-comment": "",
            "-tl": "",
            "-ff": set(),
            "-range": "",
        }

        # Parse arguments from the command
        arg_parser(input_list[1:], args)

        # Check if media tools flags are enabled
        from bot.helper.ext_utils.bot_utils import is_flag_enabled

        # Disable flags that depend on disabled media tools
        for flag in list(args.keys()):
            if flag.startswith("-") and not is_flag_enabled(flag):
                if isinstance(args[flag], bool):
                    args[flag] = False
                elif isinstance(args[flag], set):
                    args[flag] = set()
                elif isinstance(args[flag], str):
                    args[flag] = ""
                elif isinstance(args[flag], int):
                    args[flag] = 0

        try:
            # Check if multi-link operations are enabled in the configuration
            if not Config.MULTI_LINK_ENABLED and int(args["-i"]) > 0:
                await send_message(
                    self.message,
                    "❌ Multi-link operations are disabled by the administrator.",
                )
                self.multi = 0
            else:
                self.multi = int(args["-i"])
        except Exception:
            self.multi = 0

        try:
            if args["-ff"]:
                # Process multiple commands or presets
                if isinstance(args["-ff"], str):
                    # Check if it contains multiple presets separated by spaces
                    if " " in args["-ff"]:
                        preset_names = args["-ff"].split()
                        self.ffmpeg_cmds = []
                        for preset_name in preset_names:
                            # Look for preset in config
                            if (
                                Config.FFMPEG_CMDS
                                and preset_name in Config.FFMPEG_CMDS
                            ):
                                self.ffmpeg_cmds.append(
                                    Config.FFMPEG_CMDS[preset_name]
                                )
                                LOGGER.info(
                                    f"Added FFmpeg command from owner config: {preset_name}"
                                )
                            elif (
                                self.user_dict.get("FFMPEG_CMDS")
                                and preset_name in self.user_dict["FFMPEG_CMDS"]
                            ):
                                self.ffmpeg_cmds.append(
                                    self.user_dict["FFMPEG_CMDS"][preset_name]
                                )
                                LOGGER.info(
                                    f"Added FFmpeg command from user config: {preset_name}"
                                )
                            else:
                                # If not found as preset, treat as direct command
                                import shlex

                                self.ffmpeg_cmds.append(shlex.split(preset_name))
                                LOGGER.info(
                                    f"Added direct FFmpeg command: {preset_name}"
                                )
                    elif Config.FFMPEG_CMDS and args["-ff"] in Config.FFMPEG_CMDS:
                        # Single preset from owner config
                        self.ffmpeg_cmds = [Config.FFMPEG_CMDS[args["-ff"]]]
                        LOGGER.info(
                            f"Using FFmpeg command key from owner config: {self.ffmpeg_cmds}"
                        )
                    elif (
                        self.user_dict.get("FFMPEG_CMDS")
                        and args["-ff"] in self.user_dict["FFMPEG_CMDS"]
                    ):
                        # Single preset from user config
                        self.ffmpeg_cmds = [
                            self.user_dict["FFMPEG_CMDS"][args["-ff"]]
                        ]
                        LOGGER.info(
                            f"Using FFmpeg command key from user config: {self.ffmpeg_cmds}"
                        )
                    else:
                        # Direct command
                        import shlex

                        self.ffmpeg_cmds = [shlex.split(args["-ff"])]
                        LOGGER.info(
                            f"Using direct FFmpeg command: {self.ffmpeg_cmds}"
                        )
                elif isinstance(args["-ff"], set):
                    # If it's already a set, convert to list for sequential processing
                    self.ffmpeg_cmds = list(args["-ff"])
                    LOGGER.info(f"Using FFmpeg command keys: {self.ffmpeg_cmds}")
                else:
                    # For any other type, try to evaluate it
                    # This handles cases like: ["-i mltb.mkv -c copy mltb.mkv", "-i mltb.m4a -c:a libmp3lame mltb.mp3"]
                    # or [["cmd1", "arg1"], ["cmd2", "arg2"]]
                    try:
                        evaluated_cmds = eval(args["-ff"])
                        LOGGER.info(f"Evaluated FFmpeg commands: {evaluated_cmds}")
                    except Exception as e:
                        LOGGER.error(f"Error evaluating FFmpeg commands: {e}")
                        evaluated_cmds = []

                    # Handle different formats
                    if isinstance(evaluated_cmds, list):
                        # Check if it's a list of strings or a list of lists
                        if all(isinstance(item, str) for item in evaluated_cmds):
                            # List of command strings
                            import shlex

                            self.ffmpeg_cmds = [
                                shlex.split(cmd) for cmd in evaluated_cmds
                            ]
                        elif all(isinstance(item, list) for item in evaluated_cmds):
                            # List of command lists
                            self.ffmpeg_cmds = evaluated_cmds
                        else:
                            # Mixed list - try to handle each item appropriately
                            self.ffmpeg_cmds = []
                            for item in evaluated_cmds:
                                if isinstance(item, str):
                                    import shlex

                                    self.ffmpeg_cmds.append(shlex.split(item))
                                elif isinstance(item, list):
                                    self.ffmpeg_cmds.append(item)
                                else:
                                    # Try to convert to string and split
                                    import shlex

                                    self.ffmpeg_cmds.append(shlex.split(str(item)))
                    else:
                        # Single command
                        import shlex

                        self.ffmpeg_cmds = [shlex.split(str(evaluated_cmds))]

                    LOGGER.info(
                        f"Using evaluated FFmpeg commands: {self.ffmpeg_cmds}"
                    )
        except Exception as e:
            self.ffmpeg_cmds = None
            LOGGER.error(f"Error processing FFmpeg command: {e}")

        try:
            opt = eval(args["-opt"]) if args["-opt"] else {}
        except Exception as e:
            LOGGER.error(e)
            opt = {}

        self.ffmpeg_cmds = args["-ff"]
        self.select = args["-s"]
        self.name = args["-n"]
        self.up_dest = args["-up"]
        self.rc_flags = args["-rcf"]
        self.link = args["link"]
        self.compress = args["-z"]
        # Enable compression if -z flag is set and archive flags are enabled
        from bot.helper.ext_utils.bot_utils import is_flag_enabled

        if self.compress and is_flag_enabled("-z"):
            self.compression_enabled = True
        self.thumb = args["-t"]
        self.split_size = args["-sp"]
        self.sample_video = args["-sv"]
        self.screen_shots = args["-ss"]
        self.force_run = args["-f"]
        self.force_download = args["-fd"]
        self.force_upload = args["-fu"]
        self.convert_audio = args["-ca"]
        self.convert_video = args["-cv"]
        self.convert_subtitle = args["-cs"]
        self.convert_document = args["-cd"]
        self.convert_archive = args["-cr"]
        self.name_sub = args["-ns"]
        self.hybrid_leech = args["-hl"]
        self.thumbnail_layout = args["-tl"]
        self.as_doc = args["-doc"]
        self.as_med = args["-med"]
        self.metadata = args["-md"]
        self.metadata_title = args["-metadata-title"]
        self.metadata_author = args["-metadata-author"]
        self.metadata_comment = args["-metadata-comment"]
        self.metadata_all = args["-metadata-all"]
        self.metadata_video_title = args["-metadata-video-title"]
        self.metadata_video_author = args["-metadata-video-author"]
        self.metadata_video_comment = args["-metadata-video-comment"]
        self.metadata_audio_title = args["-metadata-audio-title"]
        self.metadata_audio_author = args["-metadata-audio-author"]
        self.metadata_audio_comment = args["-metadata-audio-comment"]
        self.metadata_subtitle_title = args["-metadata-subtitle-title"]
        self.metadata_subtitle_author = args["-metadata-subtitle-author"]
        self.metadata_subtitle_comment = args["-metadata-subtitle-comment"]
        self.folder_name = (
            f"/{args['-m']}".rstrip("/") if len(args["-m"]) > 0 else ""
        )
        self.bot_trans = args["-bt"]
        self.user_trans = args["-ut"]
        self.merge_video = args["-merge-video"]
        self.merge_audio = args["-merge-audio"]
        self.merge_subtitle = args["-merge-subtitle"]
        self.merge_all = args["-merge-all"]
        self.merge_image = args["-merge-image"]
        self.merge_pdf = args["-merge-pdf"]
        self.watermark = args["-watermark"]
        self.image_watermark = args["-iwm"]
        self.extract = args["-extract"]
        # Enable extract if -extract flag is set and archive flags are enabled
        if self.extract and is_flag_enabled("-extract"):
            self.extract_enabled = True
        self.extract_video = args["-extract-video"]
        self.extract_audio = args["-extract-audio"]
        self.extract_subtitle = args["-extract-subtitle"]
        self.extract_attachment = args["-extract-attachment"]
        self.add = args["-add"]
        self.add_video = args["-add-video"]
        self.add_audio = args["-add-audio"]
        self.add_subtitle = args["-add-subtitle"]
        self.add_attachment = args["-add-attachment"]
        self.trim = args["-trim"]
        self.compression = args["-compress"]
        self.comp_video = args["-comp-video"]
        self.comp_audio = args["-comp-audio"]
        self.comp_image = args["-comp-image"]
        self.comp_document = args["-comp-document"]
        self.comp_subtitle = args["-comp-subtitle"]
        self.comp_archive = args["-comp-archive"]
        self.download_range = args["-range"]

        is_bulk = args["-b"]

        bulk_start = 0
        bulk_end = 0
        reply_to = None

        if not isinstance(is_bulk, bool):
            dargs = is_bulk.split(":")
            bulk_start = dargs[0] or None
            if len(dargs) == 2:
                bulk_end = dargs[1] or None
            is_bulk = True

        if not is_bulk:
            if self.multi > 0:
                if self.folder_name:
                    async with task_dict_lock:
                        if self.folder_name in self.same_dir:
                            self.same_dir[self.folder_name]["tasks"].add(self.mid)
                            for fd_name in self.same_dir:
                                if fd_name != self.folder_name:
                                    self.same_dir[fd_name]["total"] -= 1
                        elif self.same_dir:
                            self.same_dir[self.folder_name] = {
                                "total": self.multi,
                                "tasks": {self.mid},
                            }
                            for fd_name in self.same_dir:
                                if fd_name != self.folder_name:
                                    self.same_dir[fd_name]["total"] -= 1
                        else:
                            self.same_dir = {
                                self.folder_name: {
                                    "total": self.multi,
                                    "tasks": {self.mid},
                                },
                            }
                elif self.same_dir:
                    async with task_dict_lock:
                        for fd_name in self.same_dir:
                            self.same_dir[fd_name]["total"] -= 1
        else:
            await self.init_bulk(input_list, bulk_start, bulk_end, YtDlp)
            return

        if len(self.bulk) != 0:
            del self.bulk[0]

        path = f"{DOWNLOAD_DIR}{self.mid}{self.folder_name}"

        await self.get_tag(text)

        opt = opt or self.user_dict.get("YT_DLP_OPTIONS") or Config.YT_DLP_OPTIONS

        if not self.link and (reply_to := self.message.reply_to_message):
            self.link = reply_to.text.split("\n", 1)[0].strip()

        if not is_url(self.link):
            await delete_links(self.message)
            usage_msg = await send_message(
                self.message,
                COMMAND_USAGE["yt"][0],
                COMMAND_USAGE["yt"][1],
            )
            create_task(auto_delete_message(usage_msg, time=300))  # noqa: RUF006
            await self.remove_from_same_dir()
            return

        if "mdisk.me" in self.link:
            self.name, self.link = await _mdisk(self.link, self.name)

        try:
            await self.before_start()
        except Exception as e:
            await delete_links(self.message)
            error_msg = await send_message(self.message, str(e))
            create_task(auto_delete_message(error_msg, time=300))  # noqa: RUF006
            await self.remove_from_same_dir()
            return

        # Check for user-specific cookies
        user_id = self.user_id
        user_cookies_path = f"cookies/{user_id}.txt"

        # Security check: Only use user's own cookies or the default cookies
        if ospath.exists(user_cookies_path):
            cookies_file = user_cookies_path
        else:
            cookies_file = "cookies.txt"

        options = {
            "usenetrc": True,
            "cookiefile": cookies_file,
            "ffmpeg_location": "/usr/bin/xtra",
        }
        if opt:
            for key, value in opt.items():
                if key in ["postprocessors", "download_ranges"]:
                    continue
                if key == "format" and not self.select:
                    if value.startswith("ba/b-"):
                        qual = value
                        continue
                    qual = value

                options[key] = value
        options["playlist_items"] = "0"

        # Process download range if specified
        if self.download_range:
            try:
                # Parse the range format: start_time-end_time or start_time:end_time
                # Handle cases like "30-90", "1:30-3:45", "10-", "-120", etc.
                separator = "-" if "-" in self.download_range else ":"
                range_parts = self.download_range.split(separator, 1)

                if len(range_parts) == 1:
                    # Single time value, treat as start time only
                    start_time_str = range_parts[0].strip()
                    end_time_str = ""
                elif len(range_parts) == 2:
                    start_time_str, end_time_str = [
                        part.strip() for part in range_parts
                    ]
                else:
                    raise ValueError("Invalid range format")

                # Convert time strings to seconds
                def time_to_seconds(time_str):
                    """Convert time string (HH:MM:SS, MM:SS, or SS) to seconds"""
                    time_str = time_str.strip()
                    if not time_str:
                        return None

                    parts = time_str.split(":")
                    if len(parts) == 1:  # SS
                        return int(parts[0])
                    if len(parts) == 2:  # MM:SS
                        return int(parts[0]) * 60 + int(parts[1])
                    if len(parts) == 3:  # HH:MM:SS
                        return (
                            int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                        )
                    raise ValueError("Invalid time format")

                start_seconds = (
                    time_to_seconds(start_time_str) if start_time_str else None
                )
                end_seconds = time_to_seconds(end_time_str) if end_time_str else None

                # Create download_ranges for yt-dlp
                download_range = {}
                if start_seconds is not None:
                    download_range["start_time"] = start_seconds
                if end_seconds is not None:
                    download_range["end_time"] = end_seconds

                if download_range:
                    options["download_ranges"] = lambda info, ytdl: [download_range]
                    start_display = (
                        f"{start_seconds}s" if start_seconds is not None else "start"
                    )
                    end_display = (
                        f"{end_seconds}s" if end_seconds is not None else "end"
                    )
                    LOGGER.info(
                        f"Download range set: {start_display} to {end_display}"
                    )
                else:
                    LOGGER.warning("Invalid download range format, ignoring")

            except Exception as e:
                LOGGER.error(
                    f"Error parsing download range '{self.download_range}': {e}"
                )

        # Log which cookies file is being used
        if cookies_file == user_cookies_path:
            LOGGER.info(f"Using user-specific cookies for user ID: {user_id}")
        else:
            LOGGER.info("Using default cookies.txt file")

        try:
            # Check for HLS streams and configure appropriately
            if ".m3u8" in self.link or "hls" in self.link.lower():
                LOGGER.info(
                    "HLS stream detected in ytdlp module, configuring appropriate options"
                )
                # Add HLS-specific options
                options["external_downloader"] = "xtra"
                options["hls_prefer_native"] = False
                options["hls_use_mpegts"] = True

                # For live streams
                if "live" in self.link.lower():
                    LOGGER.info(
                        "Live HLS stream detected, adding live stream options"
                    )
                    options["live_from_start"] = True
                    options["wait_for_video"] = (
                        5,
                        60,
                    )  # Wait between 5-60 seconds for video

                # Don't use YouTube-specific extractor args for HLS streams unless it's actually a YouTube link
                if (
                    "extractor_args" in options
                    and "youtube" in options["extractor_args"]
                    and not ("youtube.com" in self.link or "youtu.be" in self.link)
                ):
                    LOGGER.info(
                        "Non-YouTube HLS stream detected, removing YouTube extractor args"
                    )
                    del options["extractor_args"]["youtube"]
                    if not options["extractor_args"]:
                        del options["extractor_args"]

            # Log which client is being used for YouTube
            elif "youtube.com" in self.link or "youtu.be" in self.link:
                LOGGER.info("Extracting YouTube video info with TV client")
                # Add minimal YouTube TV client settings for initial extraction
                if "extractor_args" not in options:
                    options["extractor_args"] = {
                        "youtube": {
                            "player_client": ["tv"],
                        }
                    }
                elif "youtube" not in options["extractor_args"]:
                    options["extractor_args"]["youtube"] = {
                        "player_client": ["tv"],
                    }
                else:
                    # Ensure TV client is used even if extractor_args already exist
                    options["extractor_args"]["youtube"]["player_client"] = ["tv"]

            result = await sync_to_async(extract_info, self.link, options)

            # Debug: Log the extracted title and set it in the listener
            if result and result.get("title"):
                LOGGER.info(f"Successfully extracted title: {result['title']}")
                # Set the title in the listener so YoutubeDLHelper can use it
                if not self.name:
                    self.name = result["title"]
                    LOGGER.info(f"Set listener name to extracted title: {self.name}")
            else:
                LOGGER.warning(
                    f"Title extraction failed. Available keys: {list(result.keys()) if result else 'None'}"
                )
        except Exception as e:
            msg = str(e).replace("<", " ").replace(">", " ")

            # Check if this is an HLS stream
            is_hls = ".m3u8" in self.link or "hls" in self.link.lower()
            is_youtube = (
                "youtube" in self.link.lower() or "youtu.be" in self.link.lower()
            )

            # Handle HLS stream errors
            if is_hls and "'NoneType' object has no attribute 'can_download'" in msg:
                LOGGER.error(f"HLS stream error: {msg}")
                try:
                    # Try with different format specification
                    options["format"] = "best"
                    LOGGER.info("Retrying HLS stream with format=best")
                    result = await sync_to_async(extract_info, self.link, options)
                except Exception:
                    try:
                        # Try with different format specification
                        options["format"] = "bestvideo+bestaudio/best"
                        LOGGER.info(
                            "Retrying HLS stream with format=bestvideo+bestaudio/best"
                        )
                        result = await sync_to_async(
                            extract_info, self.link, options
                        )
                    except Exception:
                        # If all retries fail, raise a more helpful error
                        error_msg = (
                            f"Error: Failed to download HLS stream. The stream might be protected or requires authentication. "
                            f"Try downloading with a different method or check if the stream is accessible. "
                            f"Original error: {msg}"
                        )
                        raise ValueError(error_msg) from None

            # Handle YouTube SSAP experiment issues
            elif is_youtube and (
                "Unable to extract video data" in msg
                or "This video is unavailable" in msg
                or "Sign in to confirm" in msg
            ):
                try:
                    # Try with Android client
                    if (
                        "extractor_args" in options
                        and "youtube" in options["extractor_args"]
                    ):
                        options["extractor_args"]["youtube"]["player_client"] = [
                            "android"
                        ]

                    result = await sync_to_async(extract_info, self.link, options)
                except Exception:
                    try:
                        # Last resort: try with web client
                        if (
                            "extractor_args" in options
                            and "youtube" in options["extractor_args"]
                        ):
                            options["extractor_args"]["youtube"]["player_client"] = [
                                "web"
                            ]

                        result = await sync_to_async(
                            extract_info, self.link, options
                        )
                    except Exception:
                        # All clients failed, report the original error
                        msg = f"{msg}\n\nTried multiple YouTube clients but all failed. This might be due to the YouTube SSAP experiment or region restrictions."
                        try:
                            await self.on_download_error(msg)
                        except Exception as err:
                            LOGGER.error(f"Error in error handling: {err}")
                            await delete_links(self.message)
                            error_msg = await send_message(
                                self.message, f"{self.tag} {msg}"
                            )
                            create_task(auto_delete_message(error_msg, time=300))  # noqa: RUF006
                        finally:
                            await self.remove_from_same_dir()
                        return
            else:
                # Not a YouTube SSAP issue, handle normally
                try:
                    # Use self directly since YtDlp inherits from TaskListener
                    # Don't add tag here as it will be added in on_download_error
                    await self.on_download_error(msg)
                except Exception as err:
                    LOGGER.error(f"Error in error handling: {err}")
                    # Fallback error handling
                    await delete_links(self.message)
                    error_msg = await send_message(self.message, f"{self.tag} {msg}")
                    create_task(auto_delete_message(error_msg, time=300))  # noqa: RUF006
                finally:
                    await self.remove_from_same_dir()
                return
        finally:
            await self.run_multi(input_list, YtDlp)

        if not qual:
            qual = await YtSelection(self).get_quality(result)
            if qual is None:
                await self.remove_from_same_dir()
                return

        LOGGER.info(f"Downloading with YT-DLP: {self.link}")
        playlist = "entries" in result
        ydl = YoutubeDLHelper(self)
        create_task(ydl.add_download(path, qual, playlist, opt))  # noqa: RUF006
        await delete_links(self.message)
        return


async def ytdl(client, message):
    # Check if ytdlp operations are enabled in the configuration
    if not Config.YTDLP_ENABLED:
        await send_message(
            message, "❌ YT-DLP operations are disabled by the administrator."
        )
        return
    # Check if any upload service is available
    if not (
        Config.GDRIVE_UPLOAD_ENABLED
        or Config.RCLONE_ENABLED
        or Config.YOUTUBE_UPLOAD_ENABLED
        or Config.DDL_ENABLED
        or (Config.MEGA_ENABLED and Config.MEGA_UPLOAD_ENABLED)
    ):
        await send_message(
            message, "❌ All upload services are disabled by the administrator."
        )
        return
    bot_loop.create_task(YtDlp(client, message).new_event())


async def ytdl_leech(client, message):
    # Check if ytdlp operations are enabled in the configuration
    if not Config.YTDLP_ENABLED:
        await send_message(
            message, "❌ YT-DLP operations are disabled by the administrator."
        )
        return
    # Check if leech operations are enabled in the configuration
    if not Config.LEECH_ENABLED:
        await send_message(
            message, "❌ Leech operations are disabled by the administrator."
        )
        return
    bot_loop.create_task(YtDlp(client, message, is_leech=True).new_event())
