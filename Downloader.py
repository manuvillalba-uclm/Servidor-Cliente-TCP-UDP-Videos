#!/usr/bin/python -u
# -*- coding: utf-8 -*-
import os
import sys
import Ice

Ice.loadSlice('trawlnet.ice')

import TrawlNet

try:
    import youtube_dl
except ImportError:
    print('ERROR: do you have installed youtube-dl library?')
    sys.exit(1)

class NullLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

_YOUTUBEDL_OPTS_ = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': NullLogger()
}

def download_mp3(url, destination='./'):
    '''
    Synchronous download from YouTube
    '''
    options = {}
    task_status = {}
    def progress_hook(status):
        task_status.update(status)
    options.update(_YOUTUBEDL_OPTS_)
    options['progress_hooks'] = [progress_hook]
    options['outtmpl'] = os.path.join(destination, '%(title)s.%(ext)s')
    with youtube_dl.YoutubeDL(options) as youtube:
        youtube.download([url])
    filename = task_status['filename']
    # BUG: filename extension is wrong, it must be mp3
    filename = filename[:filename.rindex('.') + 1]
    return filename + options['postprocessors'][0]['preferredcodec']



class Download1(TrawlNet.Downloader):
    n = 0

    def addDownloadTask(self, message, current=None):
        print("Downloader {0}: {1}".format(self.n, message))
        sys.stdout.flush()
        self.n += 1
        download_mp3(message, "")



class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        servant = Download1()

        adapter = broker.createObjectAdapter("DownloaderAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("downloader"))

        print(proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))
