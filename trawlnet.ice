module TrawlNet {
  interface Downloader {
    string addDownloadTask(string url);
  };

  interface Orchestrator {
    string downloadTask(string url);
  };
  interface Printer {
    void write(string message);
  };
};