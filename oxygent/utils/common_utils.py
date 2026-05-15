"""The module contains some common functions."""

import asyncio
import base64
import hashlib
import json
import logging
import re
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Union
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import aiofiles
import httpx
import shortuuid
from PIL import Image
from pydantic import AnyUrl

logger = logging.getLogger(__name__)
Image.MAX_IMAGE_PIXELS = 400000000

IMAGE_EXTENSIONS = ("png", "jpg", "jpeg", "gif", "svg", "bmp", "webp", "tiff")
VIDEO_EXTENSIONS = ("mp4", "avi", "mov", "wmv", "flv", "webm", "mkv")

# HTTP headers to exclude when forwarding requests between agents.
# Used by SSEOxyAgent and A2AClientAgent to strip browser/proxy headers.
EXCLUDED_HEADERS = frozenset({
    "host",
    "connection",
    "sec-ch-ua",
    "sec-ch-ua-mobile",
    "sec-ch-ua-platform",
    "user-agent",
    "referer",
    "accept-encoding",
    "accept-language",
    "cache-control",
    "sec-fetch-site",
    "sec-fetch-mode",
    "sec-fetch-dest",
    "accept",
    "content-length",
})


def get_timestamp():
    """Return the current UNIX timestamp in milliseconds."""
    return datetime.now().timestamp() * 1000


def get_format_time():
    """Return current time as 'yyyy-MM-dd HH:mm:ss.SSSSSSSSS' with nanosecond precision."""
    now = datetime.now()
    nano_str = "{:09d}".format(now.microsecond * 1000)
    current_time = now.strftime("%Y-%m-%d %H:%M:%S.") + nano_str
    return current_time


def chunk_list(lst, chunk_size=2):
    """Split a list into chunks of the given size."""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def extract_first_json(text):
    """Extract the first JSON object from text, stripping markdown fences if present."""
    matches = re.findall(r"```[\n]*json(.*?)```", text, re.DOTALL)
    json_texts = [match.strip() for match in matches]
    json_text = json_texts[0] if json_texts else text
    if not json_text.startswith("{") or not json_text.endswith("}"):
        json_text = json_text[json_text.find("{") : json_text.rfind("}") + 1]
    return json_text


def extract_json_str(text: str) -> str:
    """Extract JSON string from text.

    Only works for single JSON string.
    """
    # NOTE: this regex parsing is taken from langchain.output_parsers.pydantic
    match = re.search(r"\{.*\}", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL)
    if not match:
        raise ValueError(f"Could not extract json string from output: {text}")

    return match.group()


async def source_to_bytes(source: str):
    """Read a URL or local file path and return its raw bytes."""
    if source.startswith("http"):
        async with httpx.AsyncClient() as client:
            http_response = await client.get(source)
            http_response.raise_for_status()
            return http_response.content
    else:
        async with aiofiles.open(source, "rb") as f:
            return await f.read()


async def image_to_base64(
    source: str, max_image_pixels: int = 10000000, base64_prefix="data:image"
) -> str:
    """Convert an image from a URL or file to a base64-encoded data URI."""
    image_bytes = await source_to_bytes(source)

    def process_image(image_bytes):
        with Image.open(BytesIO(image_bytes)) as img:
            width, height = img.size
            current_pixels = width * height

            # Proportionally resize the image to fit under max_pixels
            if current_pixels > max_image_pixels:
                scale = (max_image_pixels / current_pixels) ** 0.5
                new_width = max(1, int(width * scale))
                new_height = max(1, int(height * scale))
                img = img.resize((new_width, new_height), Image.LANCZOS)

            # Save as bytes
            output = BytesIO()
            img_format = img.format if img.format else "PNG"
            img.save(output, format=img_format)
            return output.getvalue()

    image_bytes = await asyncio.to_thread(process_image, image_bytes)
    return f"{base64_prefix};base64,{base64.b64encode(image_bytes).decode('utf-8')}"


# 512 * 1024 * 1024 bytes == 512MB
async def video_to_base64(
    source: str, max_video_size: int = 512 * 1024 * 1024, base64_prefix="data:video"
) -> str:
    """Convert a video to a base64-encoded data URI if under the size limit."""
    video_bytes = await source_to_bytes(source)
    if len(video_bytes) > max_video_size:
        return source
    return f"{base64_prefix};base64,{base64.b64encode(video_bytes).decode('utf-8')}"


def build_url(
    base_url: Union[AnyUrl, str], path: str = "", query_params: Dict[str, Any] = None
) -> str:
    """Convert base_url to a URL object, append path, and append query parameters."""
    parsed = urlparse(str(base_url))
    # Append path
    final_path = parsed.path
    if path:
        final_path = final_path.rstrip("/") + "/" + path.lstrip("/")
    # Append query
    original_query = dict(parse_qsl(parsed.query))
    query_params = query_params or {}
    merged_query = {**original_query, **query_params}
    final_query = urlencode(merged_query, doseq=True)
    # Return new url
    return urlunparse(parsed._replace(path=final_path, query=final_query))


def print_tree(node, prefix="", is_root=True, is_last=True, logger=None):
    """Recursively print a tree structure with box-drawing branch connectors."""
    # Print branch symbol
    branch = "└── " if is_last else "├── "
    if is_root:
        branch = ""
    line = prefix + branch + node.get("name", "")

    if logger:
        logger.info(line)
    else:
        print(line)

    children = node.get("children", [])
    for idx, child in enumerate(children):
        child_is_last = idx == len(children) - 1
        # Next layer prefix: uss " " for last one and "│" for others
        extension = "    " if is_last else "│   "
        if is_root:
            extension = ""
        print_tree(child, prefix + extension, False, child_is_last, logger)


def filter_json_types(d):
    """Filter a dict, replacing non-JSON-serializable values with '...'."""
    result = {}
    for k, v in d.items():
        if isinstance(v, (str, int, float, bool, list, dict, type(None))):
            result[k] = v
        else:
            result[k] = "..."
    return result


def msgpack_preprocess(obj):
    """Recursively convert an object into msgpack-serializable types."""
    # The 3 types of objects that can be serialized by msgpack
    if obj is None or isinstance(obj, (bool, int, float, str, bytes)):
        return obj
    # Tuples are converted to lists recursively
    elif isinstance(obj, (list, tuple, set)):
        return [msgpack_preprocess(item) for item in obj]
    elif isinstance(obj, dict):
        # The keys of a dict must be strings, etc
        return {str(k): msgpack_preprocess(v) for k, v in obj.items()}
    else:
        # For other types, convert to string
        return str(obj)


def get_md5(arg_str):
    """Return the MD5 hex digest of a UTF-8 encoded string."""
    md5 = hashlib.md5()
    md5.update(arg_str.encode("utf-8"))
    md5_value = md5.hexdigest()
    return md5_value


def to_json(obj):
    """Serialize an object to a JSON string, passing strings through unchanged."""
    if isinstance(obj, str):
        return obj
    return json.dumps(obj, ensure_ascii=False, default=str)


def generate_uuid(length=16):
    """Generate a short random UUID string of the given length."""
    return shortuuid.ShortUUID().random(length=length)


def is_image(source):
    """Return True if the source path has a recognized image file extension."""
    return source.split(".")[-1] in IMAGE_EXTENSIONS


def parse_mixed_string(s):
    """Parse a markdown-style string into a list of typed content segments."""
    if not isinstance(s, str):
        return s

    url_to_ext = {
        "image_url": IMAGE_EXTENSIONS,
        "video_url": VIDEO_EXTENSIONS,
    }
    ext_to_url = {ext: k for k, exts in url_to_ext.items() for ext in exts}

    # Regex match ![description](link) or ![](link)
    pattern = re.compile(r"(!)?\[([^\]]*)\]\(([^)]+)\)")
    results = []
    last_end = 0

    for match in pattern.finditer(s):
        start, end = match.span()
        # Process the preceding text segment
        if start > last_end:
            text = s[last_end:start]
            if text:
                results.append({"type": "text", "content": text})
        # Process the embedded file
        is_image = match.group(1)
        desc = match.group(2)
        link = match.group(3)
        content_type = ext_to_url.get(link.split(".")[-1], "doc_url")
        results.append(
            {
                "type": content_type,
                "content": f"{'!' if is_image else ''}[{desc}]({link})",
                "desc": desc,
                "link": link,
            }
        )
        last_end = end

    # Process the trailing text segment
    if last_end < len(s):
        text = s[last_end:]
        if text:
            results.append({"type": "text", "content": text})

    return results


def clean_ansi_codes(text):
    """Remove ANSI escape sequences from a string."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)
