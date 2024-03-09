import argparse
import os
import shutil
import tempfile
import time

import requests
import yaml

SETTINGS_PATH = os.path.expanduser("~/.config/writeme/settings.yaml")

class Client:

    def __init__(self, url, token):
        self.url = url
        self.token = token

    def get_queue(self, last_anchor=-1):
        response = requests.get(self.url + "/api/v1/queue",
                                headers={
                                    "Authorization": f"Bearer {self.token}"
                                },
                                params={
                                    "last_anchor": last_anchor,
                                    "page_size": 5,
                                })
        response.raise_for_status()
        queue = response.json()
        return queue

    def download_item(self, identifier, destination):

        filename = f"{identifier}.png"
        destination_path = os.path.join(destination, filename)

        if os.path.exists(destination_path):
            return destination_path

        with tempfile.TemporaryDirectory() as directory:
            temporary_path = os.path.join(directory, filename)
            response = requests.get(self.url + "/api/v1/queue/" + identifier,
                                    headers={
                                        "Authorization": f"Bearer {self.token}"
                                    },
                                    stream=True)
            with open(temporary_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            shutil.move(temporary_path, destination_path)
            return destination_path


def main():
    parser = argparse.ArgumentParser()
    options = parser.parse_args()

    # Load the settings.
    with open(SETTINGS_PATH) as fh:
        settings = yaml.safe_load(fh)

    # Read the settings with defaults.
    destination = os.path.expanduser(settings["destination"])
    url = settings["url"] if "url" in settings else "https://writeme.jbmorley.co.uk"
    last_anchor = settings["last_anchor"] if "last_anchor" in settings else -1
    token = settings["token"]

    # Change to the destination directory.

    # Poll the queue.
    client = Client(url=url, token=token)
    while True:
        try:
            queue = client.get_queue(last_anchor=last_anchor)
            for item in queue:
                print(item["anchor"], item["identifier"])
                client.download_item(item["identifier"], destination=destination)
                last_anchor = max(last_anchor, item["anchor"])

                # Save the last anchor.
                settings["last_anchor"] = last_anchor
                with tempfile.TemporaryDirectory() as directory:
                    temporary_path = os.path.join(directory, "settings.yaml")
                    with open(temporary_path, "w") as fh:
                        yaml.dump(settings, fh)
                    shutil.move(temporary_path, SETTINGS_PATH)

        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
            print(e)
            pass
        time.sleep(10)


if __name__ == "__main__":
    main()
