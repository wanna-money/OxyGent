from urllib.parse import urlparse, urlunparse


def ensure_url_protocol(url):
    parsed_url = urlparse(url)
    # Check if scheme is a valid protocol (http, https, ftp, etc.)
    # If no scheme or if scheme doesn't look like a protocol (e.g., 'localhost'), add http://
    if not parsed_url.scheme or (parsed_url.scheme and not parsed_url.netloc):
        # Default to 'http' protocol
        url = f'http://{url}'
        parsed_url = urlparse(url)
    return urlunparse(parsed_url)
