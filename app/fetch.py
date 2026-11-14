"""
Document fetching module for HealthLabelCheck
Downloads FSSAI regulation documents using requests with timeouts and error handling
"""

import os
import time
import requests


FSSAI_DOCUMENTS = [
    {
        "url": "https://fssai.gov.in/upload/uploadfiles/files/Compendium_Labelling_Display_04_01_2022.pdf",
        "filename": "FSSAI_Labelling_Compendium_2022.pdf",
        "description": "FSSAI Labelling and Display Compendium 2022",
    },
    {
        "url": "https://fssai.gov.in/upload/media/FSSAI_News_Packaged_FNB_04_01_2020.pdf",
        "filename": "FSSAI_Packaged_Foods_2020.pdf",
        "description": "FSSAI Packaged Food Regulations 2020",
    },
    {
        "url": "https://fssai.gov.in/upload/uploadfiles/files/Compendium_Labelling_Display_04_01_2022.pdf",
        "filename": "FSSAI_Labelling_Amendment_2021.pdf",
        "description": "FSSAI 2021 Labelling Amendment",
    },
]


def download_file(url: str, output_path: str, timeout: int = 30) -> tuple[bool, str]:
    """
    Download a file from a URL using requests with timeout and error handling.

    Args:
        url: URL to download
        output_path: Local path to save the file
        timeout: Request timeout in seconds

    Returns:
        (success, filepath_or_error_message)
    """
    try:
        print(f"  Downloading: {url}")
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        size_kb = os.path.getsize(output_path) / 1024
        print(f"  ✓ Saved {size_kb:.1f} KB → {output_path}")
        return True, output_path

    except requests.exceptions.Timeout:
        msg = f"Timeout after {timeout}s: {url}"
        print(f"  ✗ {msg}")
        return False, msg

    except requests.exceptions.ConnectionError as e:
        msg = f"Connection error: {e}"
        print(f"  ✗ {msg}")
        return False, msg

    except requests.exceptions.HTTPError as e:
        msg = f"HTTP {response.status_code}: {e}"
        print(f"  ✗ {msg}")
        return False, msg

    except Exception as e:
        msg = f"Unexpected error: {e}"
        print(f"  ✗ {msg}")
        return False, msg


def fetch_with_retry(url: str, output_path: str, max_retries: int = 3, timeout: int = 30) -> tuple[bool, str]:
    """
    Download with exponential-backoff retry.

    Returns:
        (success, filepath_or_error_message)
    """
    for attempt in range(1, max_retries + 1):
        print(f"  Attempt {attempt}/{max_retries}")
        success, result = download_file(url, output_path, timeout)
        if success:
            return True, result
        if attempt < max_retries:
            wait = 2 ** attempt
            print(f"  Waiting {wait}s before retry …")
            time.sleep(wait)

    return False, f"Failed after {max_retries} attempts"


def fetch_fssai_documents(output_dir: str = "data/raw") -> list[dict]:
    """
    Download all FSSAI documents into output_dir.

    Returns list of result dicts with keys:
        description, url, success, result
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []

    print("=== Fetching FSSAI Documents ===\n")
    for doc in FSSAI_DOCUMENTS:
        print(f"► {doc['description']}")
        output_path = os.path.join(output_dir, doc["filename"])
        success, result = fetch_with_retry(doc["url"], output_path)
        results.append(
            {
                "description": doc["description"],
                "url": doc["url"],
                "success": success,
                "result": result,
            }
        )
        print()

    return results


if __name__ == "__main__":
    results = fetch_fssai_documents()

    print("=== Fetch Summary ===")
    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"  {status} {r['description']}")
        print(f"    → {r['result']}")

