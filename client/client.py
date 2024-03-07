import argparse
import time

import requests

SERVICE_URL = "http://0.0.0.0:9449"


def get_queue(last_anchor=-1):
    response = requests.get(SERVICE_URL + "/api/v1/queue",
                            params={
                                "last_anchor": last_anchor,
                                "page_size": 5,
                            })
    queue = response.json()
    return queue


def download_item(identifier):
    response = requests.get(SERVICE_URL + "/api/v1/queue/" + identifier,
                            stream=True)
    with open(f"{identifier}.png", 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def main():
    parser = argparse.ArgumentParser()
    options = parser.parse_args()

    last_anchor = -1
    while True:
        try:
            queue = get_queue(last_anchor=last_anchor)
            for item in queue:
                print(item["anchor"], item["identifier"])
                download_item(item["identifier"])
                last_anchor = max(last_anchor, item["anchor"])
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(10)


if __name__ == "__main__":
    main()
