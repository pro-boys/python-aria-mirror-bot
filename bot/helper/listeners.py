from mega import MegaApi, MegaListener, MegaRequest
from bot import LOGGER, DOWNLOAD_DIR
from .bot_utils import get_download_status_list, get_download_index

class MirrorListeners:
    def __init__(self, context, update, reply_message):
        self.context = context
        self.update = update
        self.message = update.message
        self.reply_message = reply_message
        self.uid = update.message.message_id

    def onDownloadStarted(self, link: str):
        raise NotImplementedError

    def onDownloadProgress(self, progress_status_list: list, index: int):
        raise NotImplementedError

    def onDownloadComplete(self, progress_status_list: list, index: int):
        raise NotImplementedError

    def onDownloadError(self, error: str, progress_status_list: list, index: int):
        raise NotImplementedError

    def onUploadStarted(self, progress_status_list: list, index: int):
        raise NotImplementedError

    def onUploadComplete(self, link: str, progress_status_list: list, index: int):
        raise NotImplementedError

    def onUploadError(self, error: str, progress_status: list, index: int):
        raise NotImplementedError
