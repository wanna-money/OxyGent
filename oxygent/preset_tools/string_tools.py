"""String utility tools for OxyGent agents."""

import asyncio
import json
import re

from pydantic import Field

from oxygent.oxy import FunctionHub

string_tools = FunctionHub(name="string_tools")


@string_tools.tool(description="Extract email addresses from text")
async def extract_emails(
    text: str = Field(description="Text to extract email addresses from"),
) -> str:
    """Extract email addresses from text."""
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    emails = re.findall(email_pattern, text)
    return json.dumps(list(set(emails)), ensure_ascii=False)


@string_tools.tool(description="Extract URLs from text")
async def extract_urls(
    text: str = Field(description="Text to extract URLs from"),
) -> str:
    """Extract URLs from text."""
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    urls = re.findall(url_pattern, text)
    return json.dumps(list(set(urls)), ensure_ascii=False)


@string_tools.tool(description="Validate if a string is a valid email address")
async def validate_email(
    email: str = Field(description="Email address to validate"),
) -> str:
    """Validate email address format."""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    is_valid = bool(re.match(email_pattern, email))
    return json.dumps({"email": email, "is_valid": is_valid}, ensure_ascii=False)


# Async main function
async def main():
    # Test text data
    test_text = """
    This is some example text containing emails and URLs.
    Contact us: support@example.com or visit our website at https://www.example.com
    More info at http://info.example.org or send email to info@example.org
    Invalid email: invalid.email@ or missing@domain
    Another valid email: user.name+tag@domain.co.uk
    """

    print("=== String Tools Test Examples ===\n")

    # Test email extraction
    print("1. Extract email addresses:")
    emails_result = await extract_emails(text=test_text)
    print(f"   Input text: {test_text[:50]}...")
    print(f"   Extraction result: {emails_result}\n")

    # Test URL extraction
    print("2. Extract URLs:")
    urls_result = await extract_urls(text=test_text)
    print(f"   Input text: {test_text[:50]}...")
    print(f"   Extraction result: {urls_result}\n")

    # Test email validation
    print("3. Email address validation:")
    test_emails = [
        "support@example.com",
        "user.name+tag@domain.co.uk",
        "invalid.email@",
        "missing@domain",
        "valid@example.org",
    ]

    for email in test_emails:
        validation_result = await validate_email(email=email)
        print(f"   {email}: {validation_result}")


if __name__ == "__main__":
    # Use asyncio.run() to run the async main function
    asyncio.run(main())
