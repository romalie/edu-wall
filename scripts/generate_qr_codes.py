"""
Generate QR codes for every calendar entry and put them in Jekyll's `assets` 
directory.
"""

import argparse
import yaml
from pathlib import Path
import re
import qrcode
from rich.progress import open, track
from rich.console import Console


def strip(file_path, dir: str, extension: str):
    """
    Remove the directory in the front and the extension in the back from a path.
    """
    stripped_name = str(file_path).replace(".", "")
    stripped_name = stripped_name.replace("/", "")
    stripped_name = stripped_name.replace(dir, "")
    stripped_name = stripped_name.replace(extension, "")
    return stripped_name


def get_info(post: str):
    """
    Get ino about year, month, day and title of the post
    """
    parts = post.split("-")
    return {
        "year": parts[0],
        "month": parts[1],
        "day": parts[2],
        "title": "-".join(parts[3:]),
    }


def assemble_url(
    baseurl: str, 
    link_style: str, 
    info_dict: dict,
    extension: str = "html"
):
    """
    Create URL of a post based on the link style and info about it.
    """
    res_url = baseurl
    matches = re.findall(":([a-z_]+)", link_style)
    for match in matches:
        if match in info_dict:
            res_url += '/' + str(info_dict[match])
    
    res_url += "." + extension
    return res_url


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-p", "--posts", default="_posts", required=False,
                        help="Folder containing all the posts")
    parser.add_argument("-c", "--config", default="_config.yml", required=False,
                        help="Jekyll's config file")
    parser.add_argument("-i", "--images", default="assets/images", required=False,
                        help="Image folder to store QR codes at")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Provide verbose output")
    args = parser.parse_args()
    
    console = Console(quiet=not args.verbose)
    print = console.print
    
    with open(
        args.config, 'r', 
        description="Loading config", 
        disable=not args.verbose,
        console=console
    ) as config_file:
        config = yaml.safe_load(config_file)
        baseurl = f"{config['url']}{config['baseurl']}"
        link_style = config["permalink"]
    
    post_list = list(Path(args.posts).rglob("*.md"))
    for post_name in track(
        post_list, 
        description="Generating QRs", 
        disable=not args.verbose, 
        console=console
    ):
        post_name = strip(post_name, args.posts, "md")
        info_dict = get_info(post_name)
        post_url = assemble_url(baseurl, link_style, info_dict)
        qr = qrcode.make(post_url)
        file_name = post_name + ".png"
        qr.save(f"{args.images}/{file_name}")
        print(
            f"Generated QR code for {info_dict['year']}/{info_dict['month']} "
            f"post {info_dict['title']}. URL: {post_url}"
        )