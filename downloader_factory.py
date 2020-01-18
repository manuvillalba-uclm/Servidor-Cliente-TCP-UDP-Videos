#!/usr/bin/python -u
# -*- coding: utf-8 -*-
import os
import sys
import Ice
import IceStorm
import hashlib

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


def computeHash(filename):
    '''SHA256 hash of a file'''
    fileHash = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            fileHash.update(chunk)
    return fileHash.hexdigest()


class Download1(TrawlNet.Downloader, TrawlNet.UpdateEvent):

    events = None

    def addDownloadTask(self, message, current=None):
        print("Downloader: {0}".format( message))
        print(message[-11:])
        sys.stdout.flush()
        filename = download_mp3(message, "./downloads/")
        val = TrawlNet.FileInfo()

        val.name = message[-11:] + " - " + filename[12:]
        val.hash = computeHash(filename)
        self.events.newFile(val)
        print(self.events)
        sys.stdout.flush()

        return val

    def destroy(self, current):
        try:
            current.adapter.remove(current.id)
            print('DOWNLOADER DESTROYED')
            sys.stdout.flush()
        except Exception as e:
            print(e)
            sys.stdout.flush()


class DownloadFactory1(TrawlNet.DownloaderFactory):

    def create(self, current):
        servant = Download1()
        proxy = current.adapter.addWithUUID(servant)
        print(proxy)
        sys.stdout.flush()

        return TrawlNet.DownloaderPrx.checkedCast(proxy)


class Server(Ice.Application):

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property {} not set".format(key))
            return None

        #print("Using IceStorm in: '%s'" % key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        #Topic UpdateEvent
        topic_manager = self.communicator().stringToProxy("YoutubeDownloaderApp.IceStorm/TopicManager")
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_manager)

        if not topic_mgr:
            print('Invalid proxy')
            sys.exit()

        topic_name = "UpdateEvents"

        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        publisher = topic.getPublisher()
        
        Download1.events = TrawlNet.UpdateEventPrx.uncheckedCast(publisher)

        #Proxy directo
        broker = self.communicator()
        properties = broker.getProperties()
        servant = DownloadFactory1()

        adapter = broker.createObjectAdapter("DownloaderAdapter")

        downloader_id = properties.getProperty("DownloaderFactoryIdentity")
        proxy = adapter.add(servant, broker.stringToIdentity(downloader_id))

        print(proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))
