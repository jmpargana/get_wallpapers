#!/usr/bin/env python

"""
Fetch wallpapers from http://getwallpapers.com

This website has beautiful and high quality wallpapers
but makes you wait 5 seconds before you can download each
of them one by one. This 

Usage: pipenv run python req_wallpapers.py <type> <args>

Type:
    -c --collection - list of collections
    -q --query - search for a query and load all collection

Args:
    A list of queries or collections available in the website

"""


import os
import sys
import logging
import argparse
import requests as req
import pyperclip
from bs4 import BeautifulSoup as bs


URL = "http://getwallpapers.com/search?term="
logging.basicConfig(filename="logs.log", level=logging.INFO)


def save_image(url_and_collection):
    image_url, collection = url_and_collection

    os.makedirs(os.path.join("wallpapers", collection), exist_ok=True)

    res = req.get(image_url)

    if res.raise_for_status():
        logging.error(f"Couldn't perform get request to {image_url}")

    with open(
        os.path.join("wallpapers", collection, os.path.basename(image_url)), "wb"
    ) as f:
        logging.info(f"Saving image: {os.path.basename(image_url)}")
        for chunk in res.iter_content(100000):
            f.write(chunk)


def load_collection(image_url):
    collection = os.path.basename(image_url)
    logging.info(f"Loading collection: {collection}")

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


def load_and_search(url, query, func1, func2):
    """
        Macro to perform similar requests and search for given query
        
        Args:
            url (str): perform get request to this url
            query (str): search for all tags for a given query
            func1 (func): call this function with result
            func2 (func): parse result to call func1

        Returns:
            void

    """
    res = req.get(url)
    res.raise_for_status()
    soup = bs(res.text, "html.parser")

    for i in soup.select(query):
        func1(func2(i))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch wallpapers from http://getwallpapers.com"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--collection",
        "-c",
        nargs="+",
        type=str,
        help="List of collections (if you already know how they are called)",
    )

    group.add_argument(
        "--query",
        "-q",
        nargs="+",
        type=str,
        help="List of queries you want to search (cats for example)",
    )

    args = parser.parse_args()

    os.makedirs("wallpapers", exist_ok=True)
    tags, func = (
        (args.query, load_collections)
        if args.query
        else (args.collection, load_collection)
    )

    for tag in tags:
        func(tag)
