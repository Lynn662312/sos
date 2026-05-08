import hashlib


def generate_content_hash(text: str) -> str:
    """
    Generate a SHA-256 hex digest for the given text (UTF-8 encoded).
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    sample = "JMA alert: Earthquake early warning"
    print(generate_content_hash(sample))

