import argparse
import os
import time

import requests
import yaml

SETTINGS_PATH = os.path.expanduser("~/.config/writeme/settings.yaml")

class Client:

    def __init__(self, url):
        self.url = url

    def get_queue(self, last_anchor=-1):
        response = requests.get(self.url + "/api/v1/queue",
                                params={
                                    "last_anchor": last_anchor,
                                    "page_size": 5,
                                })
        queue = response.json()
        return queue

    def download_item(self, identifier):
        response = requests.get(self.url + "/api/v1/queue/" + identifier,
                                stream=True)
        path = f"{identifier}.png"
        if os.path.exists(path):
            return path
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return path


def main():
    parser = argparse.ArgumentParser()
    options = parser.parse_args()

    # Load the settings.
    with open(SETTINGS_PATH) as fh:
        settings = yaml.safe_load(fh)

    # Read the settings with defaults.
    destination = os.path.expanduser(settings["destination"])
    url = settings["url"] if "url" in settings else "https://writeme-staging.jbmorley.co.uk"
    last_anchor = settings["last_anchor"] if "last_anchor" in settings else -1

    # Change to the destination directory.
    os.chdir(destination)

    # Poll the queue.
    client = Client(url=url)
    while True:
        try:
            queue = client.get_queue(last_anchor=last_anchor)
            for item in queue:
                print(item["anchor"], item["identifier"])
                client.download_item(item["identifier"])
                last_anchor = max(last_anchor, item["anchor"])

                # Save the last anchor.
                settings["last_anchor"] = last_anchor
                with open(SETTINGS_PATH, "w") as fh:
                    yaml.dump(settings, fh)

        except requests.exceptions.ConnectionError:
            pass
        time.sleep(10)


if __name__ == "__main__":
    main()
