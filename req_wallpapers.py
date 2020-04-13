#!/usr/bin/env python

# Get all wallpapers from http://getwallpapers.com
# without all the waiting time to download each of them
#
# Usage: req_wallpapers.py <tags>
#
#       <tags> a list of keywords or whats saved in the clipboard


import os
import sys
import logging
import requests as req
import pyperclip
from bs4 import BeautifulSoup as bs


URL = "http://getwallpapers.com/search?term="
logging.basicConfig(filename="logs.log", level=logging.DEBUG)


def save_image(url_and_collection):
    image_url, collection = url_and_collection

    os.makedirs(os.path.join('wallpapers', collection), exist_ok=True)

    res = req.get(image_url)
    res.raise_for_status()

    with open(
        os.path.join("wallpapers", collection, os.path.basename(image_url)), "wb"
    ) as f:
        logging.debug("Saving image: {os.path.basename(image_url)}")
        for chunk in res.iter_content(100000):
            f.write(chunk)


def load_and_search(url, query, func1, func2):
    res = req.get(url)
    res.raise_for_status()
    soup = bs(res.text, "html.parser")

    for i in soup.select(query):
        func1(func2(i))


def load_collection(image_url):
    collection = os.path.basename(image_url)
    logging.debug(f"Loading collection: {collection}")

    load_and_search(
        image_url,
        ".wrapper img",
        save_image,
        lambda x: (os.path.dirname(URL) + x.get("data-src"), collection),
    )


def load_collections(tag):
    load_and_search(
        URL + tag, ".collection_thumb a", load_collection, lambda x: x.get("href")
    )


if __name__ == "__main__":
    os.makedirs("wallpapers", exist_ok=True)
    tags = sys.argv[1:] if len(sys.argv) > 1 else str(pyperclip.paste()).split()

    for tag in tags:
        logging.debug(f"Searching tag: {tag}")
        load_collections(tag)
