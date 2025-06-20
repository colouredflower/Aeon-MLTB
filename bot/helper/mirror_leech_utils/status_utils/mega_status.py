import time

from bot.helper.ext_utils.status_utils import (
    MirrorStatus,
    get_readable_file_size,
    get_readable_time,
)


class MegaDownloadStatus:
    def __init__(self, name, size, gid, obj, message, listener=None):
        self.__obj = obj
        self.__name = name
        self.__size = size
        self.__gid = gid
        self.message = message
        self.listener = listener
        self.tool = "mega"

        # Fallback: Create start time if it doesn't exist
        if not hasattr(self.__obj, "_MegaAppListener__start_time"):
            self.__obj._MegaAppListener__start_time = time.time()

    def name(self):
        return self.__name

    def progress_raw(self):
        try:
            return round(self.__obj.downloaded_bytes / self.__size * 100, 2)
        except Exception:
            return 0.0

    def progress(self):
        return f"{self.progress_raw()}%"

    def status(self):
        return MirrorStatus.STATUS_DOWNLOADING

    def processed_bytes(self):
        return get_readable_file_size(self.__obj.downloaded_bytes)

    def eta(self):
        try:
            seconds = (self.__size - self.__obj.downloaded_bytes) / self.__obj.speed
            return get_readable_time(seconds)
        except ZeroDivisionError:
            return "-"

    def size(self):
        return get_readable_file_size(self.__size)

    def speed(self):
        return f"{get_readable_file_size(self.__obj.speed)}/s"

    def downloaded_bytes(self):
        return self.__obj.downloaded_bytes

    def elapsed(self):
        try:
            # Try the standard private attribute access first
            if hasattr(self.__obj, "_MegaAppListener__start_time"):
                start_time = self.__obj._MegaAppListener__start_time
                elapsed_time = time.time() - start_time
                return get_readable_time(elapsed_time)

            # Fallback: Try to find any time-related attribute
            for attr_name in dir(self.__obj):
                if "time" in attr_name.lower() and not attr_name.startswith("__"):
                    try:
                        start_time = getattr(self.__obj, attr_name)
                        if isinstance(start_time, int | float) and start_time > 0:
                            elapsed_time = time.time() - start_time
                            return get_readable_time(elapsed_time)
                    except Exception:
                        continue

            # Last resort: return a default message
            return "Unknown"

        except Exception:
            return "Unknown"

    def gid(self):
        return self.__gid

    def task(self):
        return self.__obj

    async def cancel_task(self):
        await self.__obj.cancel_download()


class MegaUploadStatus:
    def __init__(self, name, size, gid, obj, message, listener=None):
        self.__obj = obj
        self.__name = name
        self.__size = size
        self.__gid = gid
        self.message = message
        self.listener = listener
        self.tool = "mega"

        # Fallback: Create start time if it doesn't exist
        if not hasattr(self.__obj, "_MegaAppListener__start_time"):
            self.__obj._MegaAppListener__start_time = time.time()

    def name(self):
        return self.__name

    def progress_raw(self):
        try:
            return round(self.__obj.downloaded_bytes / self.__size * 100, 2)
        except Exception:
            return 0.0

    def progress(self):
        return f"{self.progress_raw()}%"

    def status(self):
        return MirrorStatus.STATUS_UPLOADING

    def processed_bytes(self):
        return get_readable_file_size(self.__obj.downloaded_bytes)

    def eta(self):
        try:
            seconds = (self.__size - self.__obj.downloaded_bytes) / self.__obj.speed
            return get_readable_time(seconds)
        except ZeroDivisionError:
            return "-"

    def size(self):
        return get_readable_file_size(self.__size)

    def speed(self):
        return f"{get_readable_file_size(self.__obj.speed)}/s"

    def downloaded_bytes(self):
        return self.__obj.downloaded_bytes

    def elapsed(self):
        try:
            # Try the standard private attribute access first
            if hasattr(self.__obj, "_MegaAppListener__start_time"):
                start_time = self.__obj._MegaAppListener__start_time
                elapsed_time = time.time() - start_time
                return get_readable_time(elapsed_time)

            # Fallback: Try to find any time-related attribute
            for attr_name in dir(self.__obj):
                if "time" in attr_name.lower() and not attr_name.startswith("__"):
                    try:
                        start_time = getattr(self.__obj, attr_name)
                        if isinstance(start_time, int | float) and start_time > 0:
                            elapsed_time = time.time() - start_time
                            return get_readable_time(elapsed_time)
                    except Exception:
                        continue

            # Last resort: return a default message
            return "Unknown"

        except Exception:
            return "Unknown"

    def gid(self):
        return self.__gid

    def task(self):
        return self.__obj

    async def cancel_task(self):
        await self.__obj.cancel_download()


class MegaCloneStatus:
    def __init__(self, name, size, gid, obj, message, listener=None):
        self.__obj = obj
        self.__name = name
        self.__size = size
        self.__gid = gid
        self.message = message
        self.listener = listener
        self.tool = "mega"

        # Fallback: Create start time if it doesn't exist
        if not hasattr(self.__obj, "_MegaAppListener__start_time"):
            self.__obj._MegaAppListener__start_time = time.time()

    def name(self):
        return self.__name

    def progress_raw(self):
        try:
            return round(self.__obj.downloaded_bytes / self.__size * 100, 2)
        except Exception:
            return 0.0

    def progress(self):
        return f"{self.progress_raw()}%"

    def status(self):
        return MirrorStatus.STATUS_CLONING

    def processed_bytes(self):
        return get_readable_file_size(self.__obj.downloaded_bytes)

    def eta(self):
        try:
            seconds = (self.__size - self.__obj.downloaded_bytes) / self.__obj.speed
            return get_readable_time(seconds)
        except ZeroDivisionError:
            return "-"

    def size(self):
        return get_readable_file_size(self.__size)

    def speed(self):
        return f"{get_readable_file_size(self.__obj.speed)}/s"

    def downloaded_bytes(self):
        return self.__obj.downloaded_bytes

    def elapsed(self):
        try:
            # Try the standard private attribute access first
            if hasattr(self.__obj, "_MegaAppListener__start_time"):
                start_time = self.__obj._MegaAppListener__start_time
                elapsed_time = time.time() - start_time
                return get_readable_time(elapsed_time)

            # Fallback: Try to find any time-related attribute
            for attr_name in dir(self.__obj):
                if "time" in attr_name.lower() and not attr_name.startswith("__"):
                    try:
                        start_time = getattr(self.__obj, attr_name)
                        if isinstance(start_time, int | float) and start_time > 0:
                            elapsed_time = time.time() - start_time
                            return get_readable_time(elapsed_time)
                    except Exception:
                        continue

            # Last resort: return a default message
            return "Unknown"

        except Exception:
            return "Unknown"

    def gid(self):
        return self.__gid

    def task(self):
        return self.__obj

    async def cancel_task(self):
        await self.__obj.cancel_download()
