import os
from pathlib import Path
from typing import Any, Mapping

import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
PINATA_PIN_JSON_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"


def upload_to_ipfs(data: Mapping[str, Any]) -> str:
    """
    Upload a JSON-serializable mapping to IPFS via Pinata and return the CID (IpfsHash).
    """
    if not isinstance(data, Mapping):
        raise TypeError("data must be a mapping (dict-like) JSON object")

    # Keep this helper stateless: load from .env on-demand without caching globals.
    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env")

    api_key = os.getenv("PINATA_API_KEY")
    secret_key = os.getenv("PINATA_SECRET_KEY")
    if not api_key or not secret_key:
        raise RuntimeError(
            "Missing Pinata credentials. Set PINATA_API_KEY and PINATA_SECRET_KEY in .env"
        )

    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": secret_key,
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            PINATA_PIN_JSON_URL,
            headers=headers,
            json={"pinataContent": dict(data)},
            timeout=30,
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Pinata request failed: {e}") from e

    try:
        payload = resp.json()
    except ValueError:
        payload = None

    if not resp.ok:
        detail = payload if payload is not None else resp.text
        raise RuntimeError(f"Pinata pinJSONToIPFS failed ({resp.status_code}): {detail}")

    cid = (payload or {}).get("IpfsHash")
    if not cid or not isinstance(cid, str):
        raise RuntimeError(f"Unexpected Pinata response (missing IpfsHash): {payload}")

    return cid

if __name__ == "__main__":
    # Test block
    test_data = {"test": "Hello IPFS", "id": "test-123"}
    cid = upload_to_ipfs(test_data)
    print(f"📦 Uploaded! CID: {cid}")