from bot import LOGGER, MEGA_API_KEY, download_dict
import threading
from mega import (MegaApi, MegaListener, MegaRequest, MegaTransfer, MegaNode)
from bot.helper.errors import MegaDownloadError
from bot.helper.listeners import MirrorListeners
from bot.helper.mega_download_status import MegaDownloadStatus
from bot.helper.bot_utils import get_download_status_list, get_download_index
import os


class AppListener(MegaListener):

    def __init__(self, continue_event, listener: MirrorListeners):
        self.continue_event = continue_event
        self.node = None
        self.listener = listener
        super(AppListener, self).__init__()

    def onRequestStart(self, api, request):
        LOGGER.info('Request start ({})'.format(request))

    def onRequestFinish(self, api, request, error):
        LOGGER.info('Request finished ({}); Result: {}'
                    .format(request, error))

        request_type = request.getType()
        if request_type == MegaRequest.TYPE_GET_PUBLIC_NODE:
            self.node = request.getPublicMegaNode()
            if self.node is None:
                raise MegaDownloadError('Invalid mega link or link to a folder (Folder downloads not supported yet)')
        self.continue_event.set()

    def onRequestTemporaryError(self, api, request, error):
        raise MegaDownloadError(error)

    def onTransferStart(self, api: MegaApi, transfer: MegaTransfer):
        download_dict[self.listener.uid] = MegaDownloadStatus(self.listener.uid)
        download_dict[self.listener.uid].name = transfer.getFileName()
        download_dict[self.listener.uid].size = transfer.getTotalBytes()
        download_dict[self.listener.uid].status = MegaDownloadStatus.STATUS_DOWNLOADING

    def onTransferUpdate(self, api: MegaApi, transfer: MegaTransfer):
        try:
            download_dict[self.listener.uid].speed = transfer.getSpeed()
            download_dict[self.listener.uid].downloadedBytes = transfer.getTransferredBytes()
        except Exception as e:
            LOGGER.error(e)
        _list = get_download_status_list()
        self.listener.onDownloadProgress(_list, get_download_index(_list, None, self.listener.uid))


    def onTransferFinish(self, api, transfer, error):
        try:
            LOGGER.info(f'Transfer finished ({transfer}); Result: {transfer.getFileName()}')
            download_dict[self.listener.uid].status = MegaDownloadStatus.STATUS_UPLOADING
            _list = get_download_status_list()
            index = get_download_index(_list, None, self.listener.uid)
            self.listener.onDownloadComplete(_list, index)
        except Exception as e:
            LOGGER.error(e)
        self.continue_event.set()

    def onTransferTemporaryError(self, api, transfer, error):
        LOGGER.info(f'Mega download error in file {transfer} {transfer.getFileName()}: {error}')
        download_dict[self.listener.uid].status = MegaDownloadStatus.STATUS_FAILED
        raise MegaDownloadError(error)

    def onNodesUpdate(self, api, nodes):
        self.continue_event.set()


class AsyncExecutor(object):

    def __init__(self):
        self.continue_event = threading.Event()

    def do(self, function, args):
        self.continue_event.clear()
        function(*args)
        self.continue_event.wait()


def download(mega_link: str, path: str, listener):
    executor = AsyncExecutor()
    api = MegaApi(MEGA_API_KEY, None, None, 'telegram-mirror-bot')
    mega_listener = AppListener(executor.continue_event, listener)
    os.makedirs(path)
    api.addListener(mega_listener)
    executor.do(api.getPublicNode, (mega_link,))
    node = mega_listener.node
    listener.onDownloadStarted(mega_link)
    executor.do(api.startDownload, (node, path))
