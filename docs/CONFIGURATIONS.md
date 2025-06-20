## 1. Required Fields

| Variable        | Type   | Description                                                                                  |
|----------------|--------|----------------------------------------------------------------------------------------------|
| `BOT_TOKEN`     | `str`  | Telegram Bot Token obtained from [@BotFather](https://t.me/BotFather).                        |
| `OWNER_ID`      | `int`  | Telegram User ID (not username) of the bot's owner.                                           |
| `TELEGRAM_API`  | `int`  | API ID used to authenticate your Telegram account. Obtainable from [my.telegram.org](https://my.telegram.org). |
| `TELEGRAM_HASH` | `str`  | API hash used to authenticate your Telegram account. Obtainable from [my.telegram.org](https://my.telegram.org). |

## 2. Optional Fields

| Variable                  | Type           | Description |
|---------------------------|----------------|-------------|
| `TG_PROXY`                | `dict`         | Proxy settings as dict. Example: `{"scheme": "socks5", "hostname": "11.22.33.44", "port": 1234, "username": "user", "password": "pass"}`. Username/password optional. |
| `USER_SESSION_STRING`     | `str`          | Use to access Telegram premium features. Generate using `python3 generate_string_session.py`. **Note:** Use in supergroup only. |
| `DATABASE_URL`            | `str`          | MongoDB connection string. See [Create Database](https://github.com/anasty17/test?tab=readme-ov-file#create-database). Data includes bot/user settings, RSS, and tasks. |
| `CMD_SUFFIX`              | `str`          | Suffix to add at the end of all commands. |
| `AUTHORIZED_CHATS`        | `str`          | User/chat/topic IDs to authorize. Format: `chat_id`, `chat_id|thread_id`, etc. Separate by spaces. |
| `SUDO_USERS`              | `str`          | User IDs with sudo permission. Separate by spaces. |
| `UPLOAD_PATHS`            | `dict`         | Dict with upload paths. Example: `{"path 1": "remote:", "path 2": "gdrive id", ...}` |
| `DEFAULT_UPLOAD`          | `str`          | `rc` for `RCLONE_PATH`, `gd` for `GDRIVE_ID`, `ddl` for Direct Download Links. Default: `rc`. [Read More](https://github.com/anasty17/mirror-leech-telegram-bot/tree/master#upload). |
| `EXCLUDED_EXTENSIONS`     | `str`          | File extensions to skip. Separate by spaces. |
| `INCOMPLETE_TASK_NOTIFIER`| `bool`         | Notify after restart for incomplete tasks. Needs DB and supergroup. Default: `False`. |
| `FILELION_API`            | `str`          | API key from [Filelion](https://vidhide.com/?op=my_account). |
| `STREAMWISH_API`          | `str`          | API key from [Streamwish](https://streamwish.com/?op=my_account). |
| `YT_DLP_OPTIONS`          | `dict`         | Dict of `yt-dlp` options. [Docs](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L184). [Convert script](https://t.me/mltb_official_channel/177). |
| `USE_SERVICE_ACCOUNTS`    | `bool`         | Use Google API service accounts. See [guide](https://github.com/anasty17/mirror-leech-telegram-bot#generate-service-accounts-what-is-service-account). |
| `FFMPEG_CMDS`             | `dict`         | Dict with lists of ffmpeg commands. Start with arguments only. Use `-ff key` to apply. Add `-del` to auto-delete source. See example and notes. |
| `NAME_SUBSTITUTE`         | `str`          | Replace/remove words/characters using `source/target` format. Use `\` for escaping special characters. |
| `BASE_URL`                | `str`          | Base URL for the bot web interface. |
| `BASE_URL_PORT`           | `int`          | Port for the base URL. Default: `80`. |
| `INDEX_URL`               | `str`          | Index URL for file listings. |
| `TORRENT_TIMEOUT`         | `int`          | Timeout for torrent operations in seconds. Default: `0` (no timeout). |
| `STOP_DUPLICATE`          | `bool`         | Stop duplicate downloads. Default: `False`. |
| `WEB_PINCODE`             | `bool`         | Enable web interface PIN code protection. Default: `False`. |
| `UPSTREAM_REPO`           | `str`          | Upstream repository URL for updates. |
| `UPSTREAM_BRANCH`         | `str`          | Upstream repository branch. Default: `main`. |
| `HELPER_TOKENS`           | `str`          | Additional helper bot tokens for load balancing. |
| `HYPER_THREADS`           | `int`          | Number of threads for parallel processing. Default: `0` (auto). |
| `IMDB_TEMPLATE`           | `str`          | Custom template for IMDB information display. |

## 3. GDrive Tools

| Variable        | Type   | Description |
|----------------|--------|-------------|
| `GDRIVE_ID`     | `str`  | Folder/TeamDrive ID or `root`. |
| `IS_TEAM_DRIVE` | `bool` | Set `True` for TeamDrive. Default: `False`. |
| `INDEX_URL`     | `str`  | [Reference](https://gitlab.com/ParveenBhadooOfficial/Google-Drive-Index). |
| `STOP_DUPLICATE`| `bool` | Check for duplicate file/folder names. Default: `False`. |

## 4. Rclone

| Variable            | Type   | Description |
|---------------------|--------|-------------|
| `RCLONE_PATH`        | `str`  | Default upload path. |
| `RCLONE_FLAGS`       | `str`  | Use `--key:value|--key` format. [Flags](https://rclone.org/flags/). |
| `RCLONE_SERVE_URL`   | `str`  | Bot URL. Example: `http://myip` or `http://myip:port`. |
| `RCLONE_SERVE_PORT`  | `int`  | Port. Default: `8080`. |
| `RCLONE_SERVE_USER`  | `str`  | Serve username. |
| `RCLONE_SERVE_PASS`  | `str`  | Serve password. |

## 5. Update

| Variable         | Type  | Description |
|------------------|-------|-------------|
| `UPSTREAM_REPO`   | `str` | GitHub repo link. For private, use `https://username:token@github.com/username/repo`. [Get token](https://github.com/settings/tokens). |
| `UPSTREAM_BRANCH` | `str` | Branch to use. Default: `master`. |

## 6. Leech

| Variable                | Type            | Description |
|-------------------------|-----------------|-------------|
| `LEECH_SPLIT_SIZE`       | `int`           | Split size in bytes. Default: `2GB`, `4GB` for premium. |
| `AS_DOCUMENT`            | `bool`          | Upload as document. Default: `False`. |
| `USER_TRANSMISSION`      | `bool`          | Use user session for UL/DL in supergroups. Default: `False`. |
| `HYBRID_LEECH`           | `bool`          | Switch sessions based on file size. Default: `False`. |
| `LEECH_FILENAME_PREFIX`  | `str`           | Add prefix to file name. |
| `LEECH_DUMP_CHAT`        | `list[str/int]` | Chat/channel to send files. Use `-100` prefix or `chat_id|thread_id`. |
| `THUMBNAIL_LAYOUT`       | `str`           | Layout like `2x2`, `4x4`, `3x3`, etc. |
| `LEECH_SUFFIX`           | `str`           | Add suffix to file name. |
| `LEECH_FONT`             | `str`           | Default font style for leech captions. |
| `LEECH_FILENAME`         | `str`           | Custom filename template for leeched files. |
| `EQUAL_SPLITS`           | `bool`          | Create equal-sized splits. Default: `False`. |
| `MEDIA_GROUP`            | `bool`          | Send split files as media group. Default: `False`. |
| `LEECH_FILENAME_CAPTION` | `str`           | Template caption used for leeched/downloaded filenames. |

## 7. qBittorrent/Aria2c/Sabnzbd

| Variable           | Type   | Description |
|--------------------|--------|-------------|
| `TORRENT_TIMEOUT`   | `int`  | Timeout in seconds for dead torrents. |
| `BASE_URL`          | `str`  | Bot URL. Example: `http://myip` or `http://myip:port`. |
| `BASE_URL_PORT`     | `int`  | Port. Default: `80`. |
| `WEB_PINCODE`       | `bool` | Ask PIN before file selection. Default: `False`. |

## 8. JDownloader

| Variable     | Type  | Description |
|--------------|-------|-------------|
| `JD_EMAIL`    | `str` | Email for [JDownloader](https://my.jdownloader.org/). |
| `JD_PASS`     | `str` | Password. You may zip `cfg/` as `cfg.zip` and include in repo. |

## 9. Sabnzbd

| Variable        | Type   | Description |
|-----------------|--------|-------------|
| `USENET_SERVERS` | `list` | List of dicts with Usenet server config. Example:
```
[{'name': 'main', 'host': '', 'port': 563, 'timeout': 60, 'username': '', 'password': '', 'connections': 8, 'ssl': 1, 'ssl_verify': 2, 'ssl_ciphers': '', 'enable': 1, 'required': 0, 'optional': 0, 'retention': 0, 'send_group': 0, 'priority': 0}]
```
[More info](https://sabnzbd.org/wiki/configuration/4.2/servers)

## 10. RSS

| Variable         | Type         | Description |
|------------------|--------------|-------------|
| `RSS_DELAY`       | `int`        | Time interval in seconds. Default: `600`. |
| `RSS_SIZE_LIMIT`  | `int`        | Max item size in bytes. Default: `0`. |
| `RSS_CHAT`        | `str`/`int`  | Chat ID or username. Use `channel|topic` format if needed. |

**Note:** `RSS_CHAT` is mandatory. Requires either `USER_SESSION_STRING` or linked group/channel setup.

## 11. Queue System

| Variable          | Type  | Description |
|-------------------|-------|-------------|
| `QUEUE_ALL`        | `int` | Max concurrent upload + download tasks. |
| `QUEUE_DOWNLOAD`   | `int` | Max concurrent download tasks. |
| `QUEUE_UPLOAD`     | `int` | Max concurrent upload tasks. |

## 12. NZB Search

| Variable         | Type  | Description |
|------------------|-------|-------------|
| `HYDRA_IP`        | `str` | IP of [nzbhydra2](https://github.com/theotherp/nzbhydra2). |
| `HYDRA_API_KEY`   | `str` | API key from nzbhydra2. |

## 13. DDL (Direct Download Link) Upload Settings

### Basic DDL Settings
| Variable              | Type   | Description |
|-----------------------|--------|-------------|
| `DDL_ENABLED`         | `bool` | Enable/disable DDL upload feature. Default: `True`. |
| `DDL_DEFAULT_SERVER`  | `str`  | Default DDL server to use. Options: `gofile`, `streamtape`. Default: `gofile`. |

### Gofile Settings
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `GOFILE_ENABLED`            | `bool` | Enable/disable Gofile uploads. Default: `True`. |
| `GOFILE_API_KEY`            | `str`  | Default Gofile API key (can be overridden per user). Get from [Gofile](https://gofile.io/). |
| `GOFILE_FOLDER_NAME`        | `str`  | Default folder name for uploads (empty = use filename). |
| `GOFILE_PUBLIC_LINKS`       | `bool` | Generate public links by default. Default: `True`. |
| `GOFILE_PASSWORD_PROTECTION`| `bool` | Enable password protection for uploads. Default: `False`. |
| `GOFILE_DEFAULT_PASSWORD`   | `str`  | Default password for protected uploads. |
| `GOFILE_LINK_EXPIRY_DAYS`   | `int`  | Link expiry in days (0 = no expiry). Default: `0`. |

### Streamtape Settings
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMTAPE_ENABLED`        | `bool` | Enable/disable Streamtape uploads. Default: `True`. |
| `STREAMTAPE_LOGIN`          | `str`  | Default Streamtape login username. Get from [Streamtape](https://streamtape.com/). |
| `STREAMTAPE_API_KEY`        | `str`  | Default Streamtape API key. Get from [Streamtape](https://streamtape.com/). |
| `STREAMTAPE_FOLDER_NAME`    | `str`  | Default folder name for uploads. |

**Note:** DDL uploads support both Gofile and Streamtape services. Users can configure their own API keys in user settings. Streamtape only supports video files with specific extensions.

**Usage:**
- Use `-up ddl` to upload to the default DDL server
- Use `-up ddl:gofile` to upload specifically to Gofile
- Use `-up ddl:streamtape` to upload specifically to Streamtape

## 14. Streamrip Integration

### Basic Settings
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_ENABLED`         | `bool` | Enable/disable streamrip music downloading functionality. Default: `True`. |
| `STREAMRIP_CONCURRENT_DOWNLOADS` | `int` | Number of concurrent downloads. Default: `4`. |
| `STREAMRIP_MAX_SEARCH_RESULTS` | `int` | Maximum search results to display. Default: `200`. |
| `STREAMRIP_ENABLE_DATABASE` | `bool` | Enable download database tracking. Default: `True`. |
| `STREAMRIP_AUTO_CONVERT`    | `bool` | Enable automatic format conversion. Default: `True`. |
| `STREAMRIP_LIMIT`           | `float` | Download limit in GB. Default: `0` (unlimited). |

### Quality and Format Settings
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_DEFAULT_QUALITY` | `int`  | Default quality level (0-3). Default: `3` (highest). |
| `STREAMRIP_FALLBACK_QUALITY` | `int` | Fallback quality if default unavailable. Default: `2`. |
| `STREAMRIP_DEFAULT_CODEC`   | `str`  | Default audio codec. Default: `flac`. |
| `STREAMRIP_SUPPORTED_CODECS` | `list` | List of supported codecs: `["flac", "mp3", "m4a", "ogg", "opus"]`. |
| `STREAMRIP_QUALITY_FALLBACK_ENABLED` | `bool` | Enable quality fallback. Default: `True`. |

### Platform Settings
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_QOBUZ_ENABLED`   | `bool` | Enable Qobuz downloads. Default: `True`. |
| `STREAMRIP_QOBUZ_QUALITY`   | `int`  | Qobuz quality level (0-3). Default: `3`. |
| `STREAMRIP_TIDAL_ENABLED`   | `bool` | Enable Tidal downloads. Default: `True`. |
| `STREAMRIP_TIDAL_QUALITY`   | `int`  | Tidal quality level (0-3). Default: `3`. |
| `STREAMRIP_DEEZER_ENABLED`  | `bool` | Enable Deezer downloads. Default: `True`. |
| `STREAMRIP_DEEZER_QUALITY`  | `int`  | Deezer quality level (0-2). Default: `2`. |
| `STREAMRIP_SOUNDCLOUD_ENABLED` | `bool` | Enable SoundCloud downloads. Default: `True`. |
| `STREAMRIP_SOUNDCLOUD_QUALITY` | `int` | SoundCloud quality level. Default: `0`. |
| `STREAMRIP_LASTFM_ENABLED`  | `bool` | Enable Last.fm integration. Default: `True`. |
| `STREAMRIP_YOUTUBE_QUALITY` | `int`  | YouTube quality level. Default: `0`. |

### Authentication Settings
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_QOBUZ_EMAIL`     | `str`  | Qobuz account email for authentication. |
| `STREAMRIP_QOBUZ_PASSWORD`  | `str`  | Qobuz account password. |
| `STREAMRIP_QOBUZ_APP_ID`    | `str`  | Qobuz application ID for API access. |
| `STREAMRIP_QOBUZ_SECRETS`   | `list` | Qobuz application secrets list. |
| `STREAMRIP_TIDAL_EMAIL`     | `str`  | Tidal account email for authentication. |
| `STREAMRIP_TIDAL_PASSWORD`  | `str`  | Tidal account password. |
| `STREAMRIP_TIDAL_ACCESS_TOKEN` | `str` | Tidal access token for API authentication. |
| `STREAMRIP_TIDAL_REFRESH_TOKEN` | `str` | Tidal refresh token for token renewal. |
| `STREAMRIP_TIDAL_USER_ID`   | `str`  | Tidal user ID for account identification. |
| `STREAMRIP_TIDAL_COUNTRY_CODE` | `str` | Tidal country code for regional content. |
| `STREAMRIP_DEEZER_ARL`      | `str`  | Deezer ARL token for authentication. |
| `STREAMRIP_SOUNDCLOUD_CLIENT_ID` | `str` | SoundCloud client ID for API access. |
| `STREAMRIP_SOUNDCLOUD_APP_VERSION` | `str` | SoundCloud app version for compatibility. |

### Advanced Features
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_FILENAME_TEMPLATE` | `str` | Custom filename template for downloads. |
| `STREAMRIP_FOLDER_TEMPLATE` | `str`  | Custom folder structure template. |
| `STREAMRIP_EMBED_COVER_ART` | `bool` | Embed album artwork in files. Default: `True`. |
| `STREAMRIP_SAVE_COVER_ART`  | `bool` | Save separate cover art files. Default: `True`. |
| `STREAMRIP_COVER_ART_SIZE`  | `str`  | Cover art size preference. Default: `large`. |

### Download Configuration
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_MAX_CONNECTIONS` | `int`  | Maximum connections per download. Default: `6`. |
| `STREAMRIP_REQUESTS_PER_MINUTE` | `int` | API requests per minute limit. Default: `60`. |
| `STREAMRIP_SOURCE_SUBDIRECTORIES` | `bool` | Create source subdirectories. Default: `False`. |
| `STREAMRIP_DISC_SUBDIRECTORIES` | `bool` | Create disc subdirectories. Default: `True`. |
| `STREAMRIP_CONCURRENCY`     | `bool` | Enable concurrent downloads. Default: `True`. |
| `STREAMRIP_VERIFY_SSL`      | `bool` | Verify SSL certificates. Default: `True`. |

### Platform-Specific Configuration
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_QOBUZ_DOWNLOAD_BOOKLETS` | `bool` | Download PDF booklets from Qobuz. Default: `True`. |
| `STREAMRIP_QOBUZ_USE_AUTH_TOKEN` | `bool` | Use authentication token for Qobuz. Default: `False`. |
| `STREAMRIP_TIDAL_DOWNLOAD_VIDEOS` | `bool` | Download videos from Tidal. Default: `True`. |
| `STREAMRIP_TIDAL_TOKEN_EXPIRY` | `str` | Tidal token expiry timestamp. Default: `0`. |
| `STREAMRIP_DEEZER_USE_DEEZLOADER` | `bool` | Use Deezloader for Deezer. Default: `True`. |
| `STREAMRIP_DEEZER_DEEZLOADER_WARNINGS` | `bool` | Show Deezloader warnings. Default: `True`. |
| `STREAMRIP_YOUTUBE_DOWNLOAD_VIDEOS` | `bool` | Download videos from YouTube. Default: `False`. |
| `STREAMRIP_YOUTUBE_VIDEO_FOLDER` | `str` | YouTube video download folder. |
| `STREAMRIP_YOUTUBE_VIDEO_DOWNLOADS_FOLDER` | `str` | YouTube video downloads folder. |

### Database Configuration
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_DATABASE_DOWNLOADS_ENABLED` | `bool` | Enable downloads database. Default: `True`. |
| `STREAMRIP_DATABASE_DOWNLOADS_PATH` | `str` | Downloads database path. Default: `./downloads.db`. |
| `STREAMRIP_DATABASE_FAILED_DOWNLOADS_ENABLED` | `bool` | Enable failed downloads database. Default: `True`. |
| `STREAMRIP_DATABASE_FAILED_DOWNLOADS_PATH` | `str` | Failed downloads database path. Default: `./failed_downloads.db`. |

### Conversion Configuration
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_CONVERSION_ENABLED` | `bool` | Enable format conversion. Default: `False`. |
| `STREAMRIP_CONVERSION_CODEC` | `str`  | Conversion codec. Default: `ALAC`. |
| `STREAMRIP_CONVERSION_SAMPLING_RATE` | `int` | Conversion sampling rate. Default: `48000`. |
| `STREAMRIP_CONVERSION_BIT_DEPTH` | `int` | Conversion bit depth. Default: `24`. |
| `STREAMRIP_CONVERSION_LOSSY_BITRATE` | `int` | Lossy conversion bitrate. Default: `320`. |

### Filters and Metadata
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_QOBUZ_FILTERS_EXTRAS` | `bool` | Filter extra content from Qobuz. Default: `False`. |
| `STREAMRIP_QOBUZ_FILTERS_REPEATS` | `bool` | Filter repeat content. Default: `False`. |
| `STREAMRIP_QOBUZ_FILTERS_NON_ALBUMS` | `bool` | Filter non-album content. Default: `False`. |
| `STREAMRIP_QOBUZ_FILTERS_FEATURES` | `bool` | Filter featured content. Default: `False`. |
| `STREAMRIP_QOBUZ_FILTERS_NON_STUDIO_ALBUMS` | `bool` | Filter non-studio albums. Default: `False`. |
| `STREAMRIP_QOBUZ_FILTERS_NON_REMASTER` | `bool` | Filter non-remaster content. Default: `False`. |
| `STREAMRIP_ARTWORK_EMBED_MAX_WIDTH` | `int` | Max width for embedded artwork. Default: `-1` (no limit). |
| `STREAMRIP_ARTWORK_SAVED_MAX_WIDTH` | `int` | Max width for saved artwork. Default: `-1` (no limit). |
| `STREAMRIP_METADATA_SET_PLAYLIST_TO_ALBUM` | `bool` | Set playlist as album in metadata. Default: `True`. |
| `STREAMRIP_METADATA_RENUMBER_PLAYLIST_TRACKS` | `bool` | Renumber playlist tracks. Default: `True`. |
| `STREAMRIP_METADATA_EXCLUDE` | `list` | Metadata tags to exclude from files. |

### File Paths and Naming
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_FILEPATHS_ADD_SINGLES_TO_FOLDER` | `bool` | Add singles to folder. Default: `False`. |
| `STREAMRIP_FILEPATHS_FOLDER_FORMAT` | `str` | Folder naming format template. |
| `STREAMRIP_FILEPATHS_TRACK_FORMAT` | `str` | Track naming format template. |
| `STREAMRIP_FILEPATHS_RESTRICT_CHARACTERS` | `bool` | Restrict special characters in filenames. Default: `False`. |
| `STREAMRIP_FILEPATHS_TRUNCATE_TO` | `int` | Truncate filenames to length. Default: `120`. |

### Last.fm and CLI Configuration
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_LASTFM_SOURCE`   | `str`  | Last.fm source platform. Default: `qobuz`. |
| `STREAMRIP_LASTFM_FALLBACK_SOURCE` | `str` | Last.fm fallback source platform. |
| `STREAMRIP_CLI_TEXT_OUTPUT` | `bool` | Enable CLI text output. Default: `True`. |
| `STREAMRIP_CLI_PROGRESS_BARS` | `bool` | Show CLI progress bars. Default: `True`. |
| `STREAMRIP_CLI_MAX_SEARCH_RESULTS` | `int` | Max CLI search results. Default: `200`. |

### Miscellaneous
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `STREAMRIP_MISC_CHECK_FOR_UPDATES` | `bool` | Check for streamrip updates. Default: `True`. |
| `STREAMRIP_MISC_VERSION`    | `str`  | Streamrip version. Default: `2.0.6`. |

## 14. Media Tools

### Basic Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `MEDIA_TOOLS_ENABLED`   | `str`  | Comma-separated list of enabled media tools. Options: `watermark,merge,convert,compression,trim,extract,add,metadata,xtra,sample,screenshot,archive`. |
| `MEDIAINFO_ENABLED`     | `bool` | Enable/disable mediainfo command for detailed media information. Default: `False`. |
| `MEDIA_STORE`           | `bool` | Enable media storage functionality. Default: `False`. |

### Compression Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `COMPRESSION_ENABLED`   | `bool` | Enable compression functionality. Default: `False`. |
| `COMPRESSION_PRIORITY`  | `int`  | Compression task priority. Default: `4`. |
| `COMPRESSION_DELETE_ORIGINAL` | `bool` | Delete original files after compression. Default: `True`. |

### Video Compression
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `COMPRESSION_VIDEO_ENABLED` | `bool` | Enable video compression. Default: `False`. |
| `COMPRESSION_VIDEO_PRESET` | `str` | Video compression preset. Options: `none,fast,medium,slow`. Default: `none`. |
| `COMPRESSION_VIDEO_CRF` | `str`  | Video CRF (Constant Rate Factor) value. Default: `none`. |
| `COMPRESSION_VIDEO_CODEC` | `str` | Video codec for compression. Default: `none`. |
| `COMPRESSION_VIDEO_TUNE` | `str` | Video encoding tune parameter. Default: `none`. |
| `COMPRESSION_VIDEO_PIXEL_FORMAT` | `str` | Video pixel format. Default: `none`. |
| `COMPRESSION_VIDEO_BITDEPTH` | `str` | Video bit depth. Default: `none`. |
| `COMPRESSION_VIDEO_BITRATE` | `str` | Video bitrate. Default: `none`. |
| `COMPRESSION_VIDEO_RESOLUTION` | `str` | Video resolution. Default: `none`. |
| `COMPRESSION_VIDEO_FORMAT` | `str` | Output format for video compression (e.g., mp4, mkv). Default: `none`. |

### Audio Compression
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `COMPRESSION_AUDIO_ENABLED` | `bool` | Enable audio compression. Default: `False`. |
| `COMPRESSION_AUDIO_PRESET` | `str` | Audio compression preset. Options: `none,fast,medium,slow`. Default: `none`. |
| `COMPRESSION_AUDIO_CODEC` | `str` | Audio codec for compression. Default: `none`. |
| `COMPRESSION_AUDIO_BITRATE` | `str` | Audio bitrate. Default: `none`. |
| `COMPRESSION_AUDIO_CHANNELS` | `str` | Audio channels. Default: `none`. |
| `COMPRESSION_AUDIO_BITDEPTH` | `str` | Audio bit depth. Default: `none`. |
| `COMPRESSION_AUDIO_FORMAT` | `str` | Output format for audio compression (e.g., mp3, aac). Default: `none`. |

### Image Compression
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `COMPRESSION_IMAGE_ENABLED` | `bool` | Enable image compression. Default: `False`. |
| `COMPRESSION_IMAGE_PRESET` | `str` | Image compression preset. Options: `none,fast,medium,slow`. Default: `none`. |
| `COMPRESSION_IMAGE_QUALITY` | `str` | Image compression quality. Default: `none`. |
| `COMPRESSION_IMAGE_RESIZE` | `str` | Image resize dimensions. Default: `none`. |
| `COMPRESSION_IMAGE_FORMAT` | `str` | Output format for image compression (e.g., jpg, png). Default: `none`. |

### Document Compression
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `COMPRESSION_DOCUMENT_ENABLED` | `bool` | Enable document compression. Default: `False`. |
| `COMPRESSION_DOCUMENT_PRESET` | `str` | Document compression preset. Options: `none,fast,medium,slow`. Default: `none`. |
| `COMPRESSION_DOCUMENT_DPI` | `str` | Document DPI setting. Default: `none`. |
| `COMPRESSION_DOCUMENT_FORMAT` | `str` | Output format for document compression (e.g., pdf). Default: `none`. |

### Subtitle Compression
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `COMPRESSION_SUBTITLE_ENABLED` | `bool` | Enable subtitle compression. Default: `False`. |
| `COMPRESSION_SUBTITLE_PRESET` | `str` | Subtitle compression preset. Options: `none,fast,medium,slow`. Default: `none`. |
| `COMPRESSION_SUBTITLE_ENCODING` | `str` | Subtitle encoding. Default: `none`. |
| `COMPRESSION_SUBTITLE_FORMAT` | `str` | Output format for subtitle compression (e.g., srt). Default: `none`. |

### Archive Compression
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `COMPRESSION_ARCHIVE_ENABLED` | `bool` | Enable archive compression. Default: `False`. |
| `COMPRESSION_ARCHIVE_PRESET` | `str` | Archive compression preset. Options: `none,fast,medium,slow`. Default: `none`. |
| `COMPRESSION_ARCHIVE_LEVEL` | `str` | Archive compression level. Default: `none`. |
| `COMPRESSION_ARCHIVE_METHOD` | `str` | Archive compression method. Default: `none`. |
| `COMPRESSION_ARCHIVE_FORMAT` | `str` | Output format for archive compression (e.g., zip, 7z). Default: `none`. |
| `COMPRESSION_ARCHIVE_PASSWORD` | `str` | Password for archive protection. Default: `none`. |
| `COMPRESSION_ARCHIVE_ALGORITHM` | `str` | Archive algorithm (e.g., 7z, zip). Default: `none`. |

### Trim Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `TRIM_ENABLED`          | `bool` | Enable trim functionality. Default: `False`. |
| `TRIM_PRIORITY`         | `int`  | Trim task priority. Default: `5`. |
| `TRIM_START_TIME`       | `str`  | Default start time for trimming. Default: `00:00:00`. |
| `TRIM_END_TIME`         | `str`  | Default end time for trimming. |
| `TRIM_DELETE_ORIGINAL`  | `bool` | Delete original files after trimming. Default: `False`. |

### Video Trim Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `TRIM_VIDEO_ENABLED`    | `bool` | Enable video trimming. Default: `False`. |
| `TRIM_VIDEO_CODEC`      | `str`  | Video codec for trimming. Default: `none`. |
| `TRIM_VIDEO_PRESET`     | `str`  | Video encoding preset. Default: `none`. |
| `TRIM_VIDEO_FORMAT`     | `str`  | Output format for video trimming. Default: `none`. |

### Audio Trim Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `TRIM_AUDIO_ENABLED`    | `bool` | Enable audio trimming. Default: `False`. |
| `TRIM_AUDIO_CODEC`      | `str`  | Audio codec for trimming. Default: `none`. |
| `TRIM_AUDIO_PRESET`     | `str`  | Audio encoding preset. Default: `none`. |
| `TRIM_AUDIO_FORMAT`     | `str`  | Output format for audio trimming. Default: `none`. |

### Image Trim Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `TRIM_IMAGE_ENABLED`    | `bool` | Enable image trimming. Default: `False`. |
| `TRIM_IMAGE_QUALITY`    | `int`  | Image quality for trimming. Default: `90`. |
| `TRIM_IMAGE_FORMAT`     | `str`  | Output format for image trimming. Default: `none`. |

### Document Trim Settings
| Variable                    | Type   | Description |
|-----------------------------|--------|-------------|
| `TRIM_DOCUMENT_ENABLED`     | `bool` | Enable document trimming. Default: `False`. |
| `TRIM_DOCUMENT_START_PAGE`  | `str`  | Starting page number for document trimming. Default: `"1"`. |
| `TRIM_DOCUMENT_END_PAGE`    | `str`  | Ending page number for document trimming (empty for last page). Default: `""`. |
| `TRIM_DOCUMENT_QUALITY`     | `int`  | Document quality for trimming. Default: `90`. |
| `TRIM_DOCUMENT_FORMAT`      | `str`  | Output format for document trimming. Default: `none`. |

### Subtitle Trim Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `TRIM_SUBTITLE_ENABLED` | `bool` | Enable subtitle trimming. Default: `False`. |
| `TRIM_SUBTITLE_ENCODING` | `str` | Subtitle encoding. Default: `none`. |
| `TRIM_SUBTITLE_FORMAT`  | `str`  | Output format for subtitle trimming. Default: `none`. |

### Archive Trim Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `TRIM_ARCHIVE_ENABLED`  | `bool` | Enable archive trimming. Default: `False`. |
| `TRIM_ARCHIVE_FORMAT`   | `str`  | Output format for archive trimming. Default: `none`. |

### Extract Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `EXTRACT_ENABLED`       | `bool` | Enable extract functionality. Default: `False`. |
| `EXTRACT_PRIORITY`      | `int`  | Extract task priority. Default: `6`. |
| `EXTRACT_DELETE_ORIGINAL` | `bool` | Delete original files after extraction. Default: `True`. |
| `EXTRACT_MAINTAIN_QUALITY` | `bool` | Maintain quality during extraction. Default: `True`. |

### Video Extract Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `EXTRACT_VIDEO_ENABLED` | `bool` | Enable video extraction. Default: `False`. |
| `EXTRACT_VIDEO_CODEC`   | `str`  | Video codec for extraction. Default: `none`. |
| `EXTRACT_VIDEO_FORMAT`  | `str`  | Output format for video extraction. Default: `none`. |
| `EXTRACT_VIDEO_INDEX`   | `int`  | Video stream index to extract. Default: `None`. |
| `EXTRACT_VIDEO_QUALITY` | `str`  | Quality setting for video extraction. Default: `none`. |
| `EXTRACT_VIDEO_PRESET`  | `str`  | Preset for video encoding. Default: `none`. |
| `EXTRACT_VIDEO_BITRATE` | `str`  | Bitrate for video encoding. Default: `none`. |
| `EXTRACT_VIDEO_RESOLUTION` | `str` | Resolution for video extraction. Default: `none`. |
| `EXTRACT_VIDEO_FPS`     | `str`  | Frame rate for video extraction. Default: `none`. |

### Audio Extract Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `EXTRACT_AUDIO_ENABLED` | `bool` | Enable audio extraction. Default: `False`. |
| `EXTRACT_AUDIO_CODEC`   | `str`  | Audio codec for extraction. Default: `none`. |
| `EXTRACT_AUDIO_FORMAT`  | `str`  | Output format for audio extraction. Default: `none`. |
| `EXTRACT_AUDIO_INDEX`   | `int`  | Audio stream index to extract. Default: `None`. |
| `EXTRACT_AUDIO_BITRATE` | `str`  | Bitrate for audio encoding. Default: `none`. |
| `EXTRACT_AUDIO_CHANNELS` | `str` | Number of audio channels. Default: `none`. |
| `EXTRACT_AUDIO_SAMPLING` | `str` | Sampling rate for audio. Default: `none`. |
| `EXTRACT_AUDIO_VOLUME`  | `str`  | Volume adjustment for audio. Default: `none`. |

### Subtitle Extract Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `EXTRACT_SUBTITLE_ENABLED` | `bool` | Enable subtitle extraction. Default: `False`. |
| `EXTRACT_SUBTITLE_CODEC` | `str` | Subtitle codec for extraction. Default: `none`. |
| `EXTRACT_SUBTITLE_FORMAT` | `str` | Output format for subtitle extraction. Default: `none`. |
| `EXTRACT_SUBTITLE_INDEX` | `int` | Subtitle stream index to extract. Default: `None`. |
| `EXTRACT_SUBTITLE_LANGUAGE` | `str` | Language code for subtitle extraction. Default: `none`. |
| `EXTRACT_SUBTITLE_ENCODING` | `str` | Character encoding for subtitles. Default: `none`. |
| `EXTRACT_SUBTITLE_FONT` | `str` | Font for subtitles. Default: `none`. |
| `EXTRACT_SUBTITLE_FONT_SIZE` | `str` | Font size for subtitles. Default: `none`. |

### Attachment Extract Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `EXTRACT_ATTACHMENT_ENABLED` | `bool` | Enable attachment extraction. Default: `False`. |
| `EXTRACT_ATTACHMENT_FORMAT` | `str` | Output format for attachment extraction. Default: `none`. |
| `EXTRACT_ATTACHMENT_INDEX` | `int` | Attachment index to extract. Default: `None`. |
| `EXTRACT_ATTACHMENT_FILTER` | `str` | Filter for attachment extraction. Default: `none`. |

### Remove Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `REMOVE_ENABLED`        | `bool` | Enable remove functionality. Default: `False`. |
| `REMOVE_PRIORITY`       | `int`  | Remove task priority. Default: `8`. |
| `REMOVE_DELETE_ORIGINAL` | `bool` | Delete original files after removing tracks. Default: `True`. |
| `REMOVE_METADATA`       | `bool` | Remove metadata from files. Default: `False`. |
| `REMOVE_MAINTAIN_QUALITY` | `bool` | Maintain quality for remaining tracks. Default: `True`. |

### Video Remove Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `REMOVE_VIDEO_ENABLED`  | `bool` | Enable video track removal. Default: `False`. |
| `REMOVE_VIDEO_CODEC`    | `str`  | Video codec for remaining tracks. Default: `none`. |
| `REMOVE_VIDEO_FORMAT`   | `str`  | Output format for video removal. Default: `none`. |
| `REMOVE_VIDEO_INDEX`    | `int`  | Video track index to remove (supports comma-separated). Default: `None`. |
| `REMOVE_VIDEO_QUALITY`  | `str`  | Video quality for remaining tracks. Default: `none`. |
| `REMOVE_VIDEO_PRESET`   | `str`  | Video encoding preset for remaining tracks. Default: `none`. |
| `REMOVE_VIDEO_BITRATE`  | `str`  | Video bitrate for remaining tracks. Default: `none`. |
| `REMOVE_VIDEO_RESOLUTION` | `str` | Video resolution for remaining tracks. Default: `none`. |
| `REMOVE_VIDEO_FPS`      | `str`  | Video frame rate for remaining tracks. Default: `none`. |

### Audio Remove Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `REMOVE_AUDIO_ENABLED`  | `bool` | Enable audio track removal. Default: `False`. |
| `REMOVE_AUDIO_CODEC`    | `str`  | Audio codec for remaining tracks. Default: `none`. |
| `REMOVE_AUDIO_FORMAT`   | `str`  | Output format for audio removal. Default: `none`. |
| `REMOVE_AUDIO_INDEX`    | `int`  | Audio track index to remove (supports comma-separated). Default: `None`. |
| `REMOVE_AUDIO_BITRATE`  | `str`  | Audio bitrate for remaining tracks. Default: `none`. |
| `REMOVE_AUDIO_CHANNELS` | `str`  | Audio channels for remaining tracks. Default: `none`. |
| `REMOVE_AUDIO_SAMPLING` | `str`  | Audio sampling rate for remaining tracks. Default: `none`. |
| `REMOVE_AUDIO_VOLUME`   | `str`  | Audio volume adjustment for remaining tracks. Default: `none`. |

### Subtitle Remove Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `REMOVE_SUBTITLE_ENABLED` | `bool` | Enable subtitle track removal. Default: `False`. |
| `REMOVE_SUBTITLE_CODEC` | `str`  | Subtitle codec for remaining tracks. Default: `none`. |
| `REMOVE_SUBTITLE_FORMAT` | `str` | Output format for subtitle removal. Default: `none`. |
| `REMOVE_SUBTITLE_INDEX` | `int`  | Subtitle track index to remove (supports comma-separated). Default: `None`. |
| `REMOVE_SUBTITLE_LANGUAGE` | `str` | Language for remaining subtitle tracks. Default: `none`. |
| `REMOVE_SUBTITLE_ENCODING` | `str` | Character encoding for remaining subtitle tracks. Default: `none`. |
| `REMOVE_SUBTITLE_FONT`  | `str`  | Font for remaining subtitle tracks. Default: `none`. |
| `REMOVE_SUBTITLE_FONT_SIZE` | `str` | Font size for remaining subtitle tracks. Default: `none`. |

### Attachment Remove Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `REMOVE_ATTACHMENT_ENABLED` | `bool` | Enable attachment removal. Default: `False`. |
| `REMOVE_ATTACHMENT_FORMAT` | `str` | Output format for attachment removal. Default: `none`. |
| `REMOVE_ATTACHMENT_INDEX` | `int` | Attachment index to remove (supports comma-separated). Default: `None`. |
| `REMOVE_ATTACHMENT_FILTER` | `str` | Filter pattern for attachment removal. Default: `none`. |

### Add Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `ADD_ENABLED`           | `bool` | Enable add functionality. Default: `False`. |
| `ADD_PRIORITY`          | `int`  | Add task priority. Default: `7`. |
| `ADD_DELETE_ORIGINAL`   | `bool` | Delete original files after adding. Default: `True`. |
| `ADD_PRESERVE_TRACKS`   | `bool` | Preserve existing tracks when adding. Default: `False`. |
| `ADD_REPLACE_TRACKS`    | `bool` | Replace existing tracks when adding. Default: `False`. |

### Video Add Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `ADD_VIDEO_ENABLED`     | `bool` | Enable video adding. Default: `False`. |
| `ADD_VIDEO_CODEC`       | `str`  | Video codec for adding. Default: `copy`. |
| `ADD_VIDEO_INDEX`       | `int`  | Video stream index to add. Default: `None`. |
| `ADD_VIDEO_QUALITY`     | `str`  | Quality setting for video adding. Default: `none`. |
| `ADD_VIDEO_PRESET`      | `str`  | Preset for video encoding. Default: `none`. |
| `ADD_VIDEO_BITRATE`     | `str`  | Bitrate for video encoding. Default: `none`. |
| `ADD_VIDEO_RESOLUTION`  | `str`  | Resolution for video adding. Default: `none`. |
| `ADD_VIDEO_FPS`         | `str`  | Frame rate for video adding. Default: `none`. |

### Audio Add Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `ADD_AUDIO_ENABLED`     | `bool` | Enable audio adding. Default: `False`. |
| `ADD_AUDIO_CODEC`       | `str`  | Audio codec for adding. Default: `copy`. |
| `ADD_AUDIO_INDEX`       | `int`  | Audio stream index to add. Default: `None`. |
| `ADD_AUDIO_BITRATE`     | `str`  | Bitrate for audio encoding. Default: `none`. |
| `ADD_AUDIO_CHANNELS`    | `str`  | Number of audio channels. Default: `none`. |
| `ADD_AUDIO_SAMPLING`    | `str`  | Sampling rate for audio. Default: `none`. |
| `ADD_AUDIO_VOLUME`      | `str`  | Volume adjustment for audio. Default: `none`. |

### Subtitle Add Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `ADD_SUBTITLE_ENABLED`  | `bool` | Enable subtitle adding. Default: `False`. |
| `ADD_SUBTITLE_CODEC`    | `str`  | Subtitle codec for adding. Default: `copy`. |
| `ADD_SUBTITLE_INDEX`    | `int`  | Subtitle stream index to add. Default: `None`. |
| `ADD_SUBTITLE_LANGUAGE` | `str`  | Language code for subtitle adding. Default: `none`. |
| `ADD_SUBTITLE_ENCODING` | `str`  | Character encoding for subtitles. Default: `none`. |
| `ADD_SUBTITLE_FONT`     | `str`  | Font for subtitles. Default: `none`. |
| `ADD_SUBTITLE_FONT_SIZE` | `str` | Font size for subtitles. Default: `none`. |

### Attachment Add Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `ADD_ATTACHMENT_ENABLED` | `bool` | Enable attachment adding. Default: `False`. |
| `ADD_ATTACHMENT_INDEX`  | `int`  | Attachment index to add. Default: `None`. |
| `ADD_ATTACHMENT_MIMETYPE` | `str` | MIME type for attachment. Default: `none`. |

### Convert Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `CONVERT_ENABLED`       | `bool` | Enable convert functionality. Default: `False`. |
| `CONVERT_PRIORITY`      | `int`  | Convert task priority. Default: `3`. |
| `CONVERT_DELETE_ORIGINAL` | `bool` | Delete original files after conversion. Default: `True`. |

### Video Convert Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `CONVERT_VIDEO_ENABLED` | `bool` | Enable video conversion. Default: `False`. |
| `CONVERT_VIDEO_FORMAT`  | `str`  | Output format for video conversion. Default: `none`. |
| `CONVERT_VIDEO_CODEC`   | `str`  | Video codec for conversion. Default: `none`. |
| `CONVERT_VIDEO_QUALITY` | `str`  | Quality setting for video conversion. Default: `none`. |
| `CONVERT_VIDEO_CRF`     | `int`  | CRF value for video conversion. Default: `0`. |
| `CONVERT_VIDEO_PRESET`  | `str`  | Preset for video encoding. Default: `none`. |
| `CONVERT_VIDEO_MAINTAIN_QUALITY` | `bool` | Maintain quality during conversion. Default: `True`. |
| `CONVERT_VIDEO_RESOLUTION` | `str` | Resolution for video conversion. Default: `none`. |
| `CONVERT_VIDEO_FPS`     | `str`  | Frame rate for video conversion. Default: `none`. |

### Audio Convert Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `CONVERT_AUDIO_ENABLED` | `bool` | Enable audio conversion. Default: `False`. |
| `CONVERT_AUDIO_FORMAT`  | `str`  | Output format for audio conversion. Default: `none`. |
| `CONVERT_AUDIO_CODEC`   | `str`  | Audio codec for conversion. Default: `none`. |
| `CONVERT_AUDIO_BITRATE` | `str`  | Bitrate for audio encoding. Default: `none`. |
| `CONVERT_AUDIO_CHANNELS` | `int` | Number of audio channels. Default: `0`. |
| `CONVERT_AUDIO_SAMPLING` | `int` | Sampling rate for audio. Default: `0`. |
| `CONVERT_AUDIO_VOLUME`  | `float` | Volume adjustment for audio. Default: `0.0`. |

### Subtitle Convert Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `CONVERT_SUBTITLE_ENABLED` | `bool` | Enable subtitle conversion. Default: `False`. |
| `CONVERT_SUBTITLE_FORMAT` | `str` | Output format for subtitle conversion. Default: `none`. |
| `CONVERT_SUBTITLE_ENCODING` | `str` | Character encoding for subtitles. Default: `none`. |
| `CONVERT_SUBTITLE_LANGUAGE` | `str` | Language code for subtitle conversion. Default: `none`. |

### Document Convert Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `CONVERT_DOCUMENT_ENABLED` | `bool` | Enable document conversion. Default: `False`. |
| `CONVERT_DOCUMENT_FORMAT` | `str` | Output format for document conversion. Default: `none`. |
| `CONVERT_DOCUMENT_QUALITY` | `int` | Quality setting for document conversion. Default: `0`. |
| `CONVERT_DOCUMENT_DPI`  | `int`  | DPI setting for document conversion. Default: `0`. |

### Archive Convert Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `CONVERT_ARCHIVE_ENABLED` | `bool` | Enable archive conversion. Default: `False`. |
| `CONVERT_ARCHIVE_FORMAT` | `str` | Output format for archive conversion. Default: `none`. |
| `CONVERT_ARCHIVE_LEVEL` | `int`  | Compression level for archive conversion. Default: `0`. |
| `CONVERT_ARCHIVE_METHOD` | `str` | Compression method for archive conversion. Default: `none`. |

### Watermark Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `WATERMARK_ENABLED`     | `bool` | Enable watermark functionality. Default: `False`. |
| `WATERMARK_KEY`         | `str`  | Key used for watermarking files or content. |
| `WATERMARK_POSITION`    | `str`  | Watermark position. Default: `none`. |
| `WATERMARK_SIZE`        | `int`  | Watermark size. Default: `0`. |
| `WATERMARK_COLOR`       | `str`  | Watermark color. Default: `none`. |
| `WATERMARK_FONT`        | `str`  | Watermark font. Default: `none`. |
| `WATERMARK_PRIORITY`    | `int`  | Watermark task priority. Default: `2`. |
| `WATERMARK_THREADING`   | `bool` | Enable watermark threading. Default: `True`. |
| `WATERMARK_THREAD_NUMBER` | `int` | Number of watermark threads. Default: `4`. |
| `WATERMARK_QUALITY`     | `str`  | Watermark quality setting. Default: `none`. |
| `WATERMARK_SPEED`       | `str`  | Watermark processing speed. Default: `none`. |
| `WATERMARK_OPACITY`     | `float` | Watermark opacity. Default: `0.0`. |
| `WATERMARK_REMOVE_ORIGINAL` | `bool` | Remove original files after watermarking. Default: `True`. |

### Audio Watermark Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `AUDIO_WATERMARK_VOLUME` | `float` | Audio watermark volume. Default: `0.0`. |
| `AUDIO_WATERMARK_INTERVAL` | `int` | Audio watermark interval. Default: `0`. |

### Subtitle Watermark Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `SUBTITLE_WATERMARK_STYLE` | `str` | Subtitle watermark style. Default: `none`. |
| `SUBTITLE_WATERMARK_INTERVAL` | `int` | Subtitle watermark interval. Default: `0`. |

### Image Watermark Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `IMAGE_WATERMARK_ENABLED` | `bool` | Enable image watermarking. Default: `False`. |
| `IMAGE_WATERMARK_PATH`  | `str`  | Path to watermark image. |
| `IMAGE_WATERMARK_SCALE` | `int`  | Image watermark scale percentage. Default: `10`. |
| `IMAGE_WATERMARK_OPACITY` | `float` | Image watermark opacity. Default: `1.0`. |
| `IMAGE_WATERMARK_POSITION` | `str` | Image watermark position. Default: `bottom_right`. |

### Merge Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `MERGE_ENABLED`         | `bool` | Enable merge functionality. Default: `False`. |
| `MERGE_PRIORITY`        | `int`  | Merge task priority. Default: `1`. |
| `MERGE_THREADING`       | `bool` | Enable merge threading. Default: `True`. |
| `MERGE_THREAD_NUMBER`   | `int`  | Number of merge threads. Default: `4`. |
| `CONCAT_DEMUXER_ENABLED` | `bool` | Enable concat demuxer. Default: `True`. |
| `FILTER_COMPLEX_ENABLED` | `bool` | Enable filter complex. Default: `False`. |
| `MERGE_REMOVE_ORIGINAL` | `bool` | Remove original files after merging. Default: `True`. |

### Merge Output Formats
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `MERGE_OUTPUT_FORMAT_VIDEO` | `str` | Output format for video merging. Default: `none`. |
| `MERGE_OUTPUT_FORMAT_AUDIO` | `str` | Output format for audio merging. Default: `none`. |
| `MERGE_OUTPUT_FORMAT_IMAGE` | `str` | Output format for image merging. Default: `none`. |
| `MERGE_OUTPUT_FORMAT_DOCUMENT` | `str` | Output format for document merging. Default: `none`. |
| `MERGE_OUTPUT_FORMAT_SUBTITLE` | `str` | Output format for subtitle merging. Default: `none`. |

### Merge Video Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `MERGE_VIDEO_CODEC`     | `str`  | Video codec for merging. Default: `none`. |
| `MERGE_VIDEO_QUALITY`   | `str`  | Video quality for merging. Default: `none`. |
| `MERGE_VIDEO_PRESET`    | `str`  | Video preset for merging. Default: `none`. |
| `MERGE_VIDEO_CRF`       | `str`  | Video CRF for merging. Default: `none`. |
| `MERGE_VIDEO_PIXEL_FORMAT` | `str` | Video pixel format for merging. Default: `none`. |
| `MERGE_VIDEO_TUNE`      | `str`  | Video tune setting for merging. Default: `none`. |
| `MERGE_VIDEO_FASTSTART` | `bool` | Enable video faststart for merging. Default: `False`. |

### Merge Audio Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `MERGE_AUDIO_CODEC`     | `str`  | Audio codec for merging. Default: `none`. |
| `MERGE_AUDIO_BITRATE`   | `str`  | Audio bitrate for merging. Default: `none`. |
| `MERGE_AUDIO_CHANNELS`  | `str`  | Audio channels for merging. Default: `none`. |
| `MERGE_AUDIO_SAMPLING`  | `str`  | Audio sampling rate for merging. Default: `none`. |
| `MERGE_AUDIO_VOLUME`    | `str`  | Audio volume for merging. Default: `none`. |

### Merge Image Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `MERGE_IMAGE_MODE`      | `str`  | Image merge mode. Default: `none`. |
| `MERGE_IMAGE_COLUMNS`   | `str`  | Image columns for merging. Default: `none`. |
| `MERGE_IMAGE_QUALITY`   | `int`  | Image quality for merging. Default: `0`. |
| `MERGE_IMAGE_DPI`       | `str`  | Image DPI for merging. Default: `none`. |
| `MERGE_IMAGE_RESIZE`    | `str`  | Image resize for merging. Default: `none`. |
| `MERGE_IMAGE_BACKGROUND` | `str` | Image background for merging. Default: `none`. |

### Merge Subtitle Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `MERGE_SUBTITLE_ENCODING` | `str` | Subtitle encoding for merging. Default: `none`. |
| `MERGE_SUBTITLE_FONT`   | `str`  | Subtitle font for merging. Default: `none`. |
| `MERGE_SUBTITLE_FONT_SIZE` | `str` | Subtitle font size for merging. Default: `none`. |
| `MERGE_SUBTITLE_FONT_COLOR` | `str` | Subtitle font color for merging. Default: `none`. |
| `MERGE_SUBTITLE_BACKGROUND` | `str` | Subtitle background for merging. Default: `none`. |

### Merge Document Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `MERGE_DOCUMENT_PAPER_SIZE` | `str` | Document paper size for merging. Default: `none`. |
| `MERGE_DOCUMENT_ORIENTATION` | `str` | Document orientation for merging. Default: `none`. |
| `MERGE_DOCUMENT_MARGIN` | `str`  | Document margin for merging. Default: `none`. |

### Merge Metadata Settings
| Variable                | Type   | Description |
|-------------------------|--------|-------------|
| `MERGE_METADATA_TITLE`  | `str`  | Metadata title for merged files. Default: `none`. |
| `MERGE_METADATA_AUTHOR` | `str`  | Metadata author for merged files. Default: `none`. |
| `MERGE_METADATA_COMMENT` | `str` | Metadata comment for merged files. Default: `none`. |

## 15. AI Integration

| Variable          | Type   | Description |
|-------------------|--------|-------------|
| `AI_ENABLED`      | `bool` | Enable/disable AI chat functionality. Default: `False`. |
| `AI_PROVIDER`     | `str`  | AI provider to use. Options: `mistral,deepseek,custom`. |
| `AI_API_KEY`      | `str`  | API key for the AI provider. |
| `AI_API_URL`      | `str`  | Custom API URL for AI provider (if using custom). |
| `AI_MODEL`        | `str`  | AI model to use for responses. |
| `AI_MAX_TOKENS`   | `int`  | Maximum tokens per AI response. Default: `1000`. |

## 16. Security Tools

| Variable              | Type   | Description |
|-----------------------|--------|-------------|
| `VIRUSTOTAL_API_KEY`  | `str`  | VirusTotal API key for malware scanning. |
| `TRUECALLER_API_KEY`  | `str`  | Truecaller API key for phone number lookup. |
| `SECURITY_SCAN_AUTO`  | `bool` | Automatically scan downloaded files. Default: `False`. |

## 17. Font Styles

| Variable              | Type   | Description |
|-----------------------|--------|-------------|
| `DEFAULT_FONT_STYLE`  | `str`  | Default font style for leech captions. |
| `FONT_STYLES_ENABLED` | `bool` | Enable/disable font styling functionality. Default: `True`. |
| `CUSTOM_FONTS`        | `dict` | Custom font definitions as JSON dict. |

## 18. Limits and Monitoring

### Storage and Download Limits
| Variable               | Type   | Description |
|------------------------|--------|-------------|
| `STORAGE_THRESHOLD`    | `float` | Storage threshold in GB. Default: `0` (no limit). |
| `TORRENT_LIMIT`        | `float` | Torrent download limit in GB. Default: `0` (no limit). |
| `DIRECT_LIMIT`         | `float` | Direct download limit in GB. Default: `0` (no limit). |
| `YTDLP_LIMIT`          | `float` | YT-DLP download limit in GB. Default: `0` (no limit). |
| `GDRIVE_LIMIT`         | `float` | Google Drive operation limit in GB. Default: `0` (no limit). |
| `CLONE_LIMIT`          | `float` | Clone operation limit in GB. Default: `0` (no limit). |
| `MEGA_LIMIT`           | `float` | MEGA download limit in GB. Default: `0` (no limit). |
| `LEECH_LIMIT`          | `float` | Leech operation limit in GB. Default: `0` (no limit). |
| `JD_LIMIT`             | `float` | JDownloader limit in GB. Default: `0` (no limit). |
| `NZB_LIMIT`            | `float` | NZB download limit in GB. Default: `0` (no limit). |
| `PLAYLIST_LIMIT`       | `int`  | Maximum number of videos in playlist. Default: `0` (no limit). |

### Daily Limits
| Variable               | Type   | Description |
|------------------------|--------|-------------|
| `DAILY_TASK_LIMIT`     | `int`  | Number of tasks per day per user. Default: `0` (no limit). |
| `DAILY_MIRROR_LIMIT`   | `float` | GB per day for mirror operations. Default: `0` (no limit). |
| `DAILY_LEECH_LIMIT`    | `float` | GB per day for leech operations. Default: `0` (no limit). |

### User and Bot Limits
| Variable               | Type   | Description |
|------------------------|--------|-------------|
| `USER_MAX_TASKS`       | `int`  | Maximum concurrent tasks per user. Default: `0` (no limit). |
| `USER_TIME_INTERVAL`   | `int`  | Seconds between tasks for users. Default: `0` (no limit). |
| `BOT_MAX_TASKS`        | `int`  | Maximum concurrent tasks the bot can handle. Default: `0` (no limit). |
| `STATUS_LIMIT`         | `int`  | Number of tasks to display in status message. Default: `10`. |
| `SEARCH_LIMIT`         | `int`  | Maximum number of search results to display. Default: `0` (no limit). |
| `SHOW_CLOUD_LINK`      | `bool` | Show cloud links in upload completion message. Default: `True`. |

### Task Monitoring
| Variable               | Type   | Description |
|------------------------|--------|-------------|
| `TASK_MONITOR_ENABLED` | `bool` | Enable task monitoring system. Default: `True`. |
| `TASK_MONITOR_INTERVAL` | `int` | Monitoring interval in seconds. Default: `60`. |
| `TASK_MONITOR_CONSECUTIVE_CHECKS` | `int` | Consecutive checks before action. Default: `20`. |
| `TASK_MONITOR_SPEED_THRESHOLD` | `int` | Speed threshold in KB/s. Default: `50`. |
| `TASK_MONITOR_ELAPSED_THRESHOLD` | `int` | Elapsed time threshold in seconds. Default: `3600`. |
| `TASK_MONITOR_ETA_THRESHOLD` | `int` | ETA threshold in seconds. Default: `86400`. |
| `TASK_MONITOR_WAIT_TIME` | `int` | Wait time in seconds. Default: `600`. |
| `TASK_MONITOR_COMPLETION_THRESHOLD` | `int` | Completion threshold in seconds. Default: `86400`. |
| `TASK_MONITOR_CPU_HIGH` | `int` | High CPU usage percentage. Default: `90`. |
| `TASK_MONITOR_CPU_LOW` | `int` | Low CPU usage percentage. Default: `60`. |
| `TASK_MONITOR_MEMORY_HIGH` | `int` | High memory usage percentage. Default: `75`. |
| `TASK_MONITOR_MEMORY_LOW` | `int` | Low memory usage percentage. Default: `60`. |

### Auto Restart Settings
| Variable               | Type   | Description |
|------------------------|--------|-------------|
| `AUTO_RESTART_ENABLED` | `bool` | Enable automatic restart functionality. Default: `False`. |
| `AUTO_RESTART_INTERVAL` | `int` | Auto restart interval in hours. Default: `24`. |

## 19. Feature Toggles

### Core Features
| Variable               | Type   | Description |
|------------------------|--------|-------------|
| `ENABLE_EXTRA_MODULES` | `bool` | Enable extra modules functionality. Default: `True`. |
| `MULTI_LINK_ENABLED`   | `bool` | Enable multi-link download support. Default: `True`. |
| `SAME_DIR_ENABLED`     | `bool` | Enable same directory functionality. Default: `True`. |
| `MIRROR_ENABLED`       | `bool` | Enable mirror functionality. Default: `True`. |
| `LEECH_ENABLED`        | `bool` | Enable leech functionality. Default: `True`. |
| `YTDLP_ENABLED`        | `bool` | Enable YT-DLP functionality. Default: `True`. |
| `TORRENT_ENABLED`      | `bool` | Enable torrent functionality. Default: `True`. |
| `TORRENT_SEARCH_ENABLED` | `bool` | Enable torrent search functionality. Default: `True`. |
| `NZB_ENABLED`          | `bool` | Enable NZB functionality. Default: `True`. |
| `NZB_SEARCH_ENABLED`   | `bool` | Enable NZB search functionality. Default: `True`. |
| `JD_ENABLED`           | `bool` | Enable JDownloader functionality. Default: `True`. |
| `HYPERDL_ENABLED`      | `bool` | Enable Hyper Download functionality. Default: `True`. |
| `MEDIA_SEARCH_ENABLED` | `bool` | Enable media search functionality. Default: `True`. |
| `RCLONE_ENABLED`       | `bool` | Enable Rclone functionality. Default: `True`. |
| `ARCHIVE_FLAGS_ENABLED` | `bool` | Enable archive operation flags. Default: `True`. |
| `BULK_ENABLED`         | `bool` | Enable bulk operations (-b flag). Default: `True`. |

## 20. AI and External Services

### AI Configuration
| Variable               | Type   | Description |
|------------------------|--------|-------------|
| `DEFAULT_AI_PROVIDER`  | `str`  | Default AI provider (mistral, deepseek). Default: `mistral`. |
| `MISTRAL_API_URL`      | `str`  | Mistral AI API URL. |
| `DEEPSEEK_API_URL`     | `str`  | DeepSeek AI API URL. |

### Security Tools
| Variable               | Type   | Description |
|------------------------|--------|-------------|
| `VT_API_KEY`           | `str`  | VirusTotal API key for malware scanning. |
| `VT_API_TIMEOUT`       | `int`  | VirusTotal API timeout in seconds. Default: `500`. |
| `VT_ENABLED`           | `bool` | Enable VirusTotal functionality. Default: `False`. |
| `VT_MAX_FILE_SIZE`     | `int`  | Maximum file size for VirusTotal scanning in bytes. Default: `33554432` (32MB). |
| `TRUECALLER_API_URL`   | `str`  | Truecaller API URL for phone number lookup. |

### Command Management
| Variable               | Type   | Description |
|------------------------|--------|-------------|
| `CORRECT_CMD_SUFFIX`   | `str`  | Comma-separated list of allowed command suffixes. |
| `WRONG_CMD_WARNINGS_ENABLED` | `bool` | Enable/disable warnings for wrong command suffixes. Default: `True`. |

## 21. Extra fields from Aeon

| Variable               | Type   | Description |
|------------------------|--------|-------------|
| `METADATA_KEY`         | `str`  | Key used to tag or fetch metadata. |
| `WATERMARK_KEY`        | `str`  | Key used for watermarking files or content. |
| `METADATA_ALL`         | `str`  | Global metadata for all fields. |
| `METADATA_TITLE`       | `str`  | Global title metadata. |
| `METADATA_AUTHOR`      | `str`  | Global author metadata. |
| `METADATA_COMMENT`     | `str`  | Global comment metadata. |
| `METADATA_VIDEO_TITLE` | `str`  | Video track title metadata. |
| `METADATA_VIDEO_AUTHOR` | `str` | Video track author metadata. |
| `METADATA_VIDEO_COMMENT` | `str` | Video track comment metadata. |
| `METADATA_AUDIO_TITLE` | `str`  | Audio track title metadata. |
| `METADATA_AUDIO_AUTHOR` | `str` | Audio track author metadata. |
| `METADATA_AUDIO_COMMENT` | `str` | Audio track comment metadata. |
| `METADATA_SUBTITLE_TITLE` | `str` | Subtitle track title metadata. |
| `METADATA_SUBTITLE_AUTHOR` | `str` | Subtitle track author metadata. |
| `METADATA_SUBTITLE_COMMENT` | `str` | Subtitle track comment metadata. |
| `SET_COMMANDS`         | `bool` | Whether to register bot commands on startup. Default: `True`. |
| `TOKEN_TIMEOUT`        | `int`  | Timeout in seconds for token/session expiry. Default: `0`. |
| `PAID_CHANNEL_ID`      | `int`  | Telegram channel ID where user need to join for no token. Default: `0`. |
| `PAID_CHANNEL_LINK`    | `str`  | Invite or public link to the paid Telegram channel. |
| `DELETE_LINKS`         | `bool` | Whether to auto-delete download or share links. Default: `False`. |
| `FSUB_IDS`             | `str`  | Comma-separated IDs of forced subscription channels. |
| `LOG_CHAT_ID`          | `int`  | Chat ID where leech logs sent. Default: `0`. |
| `LEECH_FILENAME_CAPTION` | `str` | Template caption used for leeched/downloaded filenames. |
| `INSTADL_API`          | `str`  | URL or endpoint for InstaDL API integration. |
| `HEROKU_APP_NAME`      | `str`  | Name of the Heroku app for get `BASE_URL` automatically. |
| `HEROKU_API_KEY`       | `str`  | API key for accessing and controlling Heroku. |
| `LOGIN_PASS`           | `str`  | Password for web login authentication. |
| `AD_KEYWORDS`          | `str`  | Custom keywords/phrases for ad detection, separated by comma. |
| `AD_BROADCASTER_ENABLED` | `bool` | Enable/disable automatic ad broadcasting from FSUB channels to users. Default: `False`. |
| `CREDIT`               | `str`  | Credit text shown in status messages and RSS feeds. Default: `Powered by @aimmirror`. |
| `OWNER_THUMB`          | `str`  | Default thumbnail URL for owner. Default: `https://graph.org/file/80b7fb095063a18f9e232.jpg`. |
| `PIL_MEMORY_LIMIT`     | `int`  | PIL memory limit in MB. Default: `2048`. |
| `MEDIA_SEARCH_CHATS`   | `list` | List of chat IDs for media search functionality. |
