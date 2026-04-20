"""
Wolfram Alpha API integration module.
Handles credential storage, query execution, and result parsing.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
import xml.etree.ElementTree as ET
from pathlib import Path

# ─── Credential Management ───────────────────────────────────────

def _get_keyring_path():
    """Get platform-specific keyring info."""
    try:
        import keyring
        return keyring
    except ImportError:
        return None


def _get_fallback_key_file():
    """Get fallback credential file path."""
    key_dir = Path.home() / ".wolframalpha"
    key_dir.mkdir(exist_ok=True)
    return key_dir / "key"


def load_api_key():
    """Load API key from keyring or fallback file. Returns None if not found."""
    keyring = _get_keyring_path()
    
    if keyring:
        try:
            key = keyring.get_password("wolframalpha", "app_id")
            if key:
                return key
        except Exception:
            pass
    
    key_file = _get_fallback_key_file()
    if key_file.exists():
        try:
            return key_file.read_text().strip()
        except Exception:
            pass
    
    return None


def save_api_key(key):
    """Save API key to keyring or fallback file."""
    keyring = _get_keyring_path()
    
    if keyring:
        try:
            keyring.set_password("wolframalpha", "app_id", key)
            return {"success": True, "message": "API key saved securely."}
        except Exception:
            pass
    
    key_file = _get_fallback_key_file()
    try:
        key_file.write_text(key)
        msg = "API key saved to file (consider installing 'keyring' for better security)."
        return {"success": True, "message": msg}
    except Exception as e:
        return {"success": False, "message": f"Failed to save API key: {str(e)}"}


def clear_api_key():
    """Clear saved API key from both keyring and fallback file."""
    keyring = _get_keyring_path()
    
    if keyring:
        try:
            keyring.delete_password("wolframalpha", "app_id")
        except Exception:
            pass
    
    key_file = _get_fallback_key_file()
    try:
        if key_file.exists():
            key_file.unlink()
    except Exception:
        pass
    
    return {"success": True, "message": "API key cleared."}


def _build_query_url(app_id, query_text, assumptions=None):
    """Build a raw Wolfram Alpha query URL with plaintext output."""
    params = [
        ("appid", app_id),
        ("input", query_text),
        ("format", "plaintext"),
    ]
    if assumptions:
        for assumption in assumptions:
            if assumption and assumption.strip():
                params.append(("assumption", assumption.strip()))
    return "https://api.wolframalpha.com/v2/query?" + urllib.parse.urlencode(params, doseq=True)


def _execute_raw_query(app_id, query_text, assumptions=None):
    """Execute a raw HTTP request against the Wolfram Alpha API."""
    url = _build_query_url(app_id.strip(), query_text.strip(), assumptions)
    request = urllib.request.Request(url, headers={"User-Agent": "Python/WolframAlpha"})

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read()
            return {
                "success": True,
                "status": response.status,
                "content_type": response.headers.get("Content-Type", ""),
                "body": body,
            }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "status": e.code,
            "content_type": e.headers.get("Content-Type", "") if e.headers else "",
            "body": e.read() if hasattr(e, "read") else b"",
            "error": str(e),
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": str(e.reason) if hasattr(e, "reason") else str(e),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def _parse_raw_response(body):
    """Parse Wolfram Alpha XML response and return structured pod results."""
    root = ET.fromstring(body)
    success = root.attrib.get("success", "false").lower() == "true"
    error_message = None

    if not success:
        error_node = root.find("error/msg")
        if error_node is not None and error_node.text:
            error_message = error_node.text.strip()
        else:
            did_you_means = [dym.text.strip() for dym in root.findall("didyoumeans/didyoumean") if dym.text]
            if did_you_means:
                error_message = "Did you mean: " + ", ".join(did_you_means)
            else:
                error_message = "No results found."

    pods = []
    for pod in root.findall("pod"):
        pod_title = pod.attrib.get("title", "Unknown")
        pod_id = pod.attrib.get("id", "")
        subpod_data = []
        for subpod in pod.findall("subpod"):
            plaintext_node = subpod.find("plaintext")
            plaintext = plaintext_node.text.strip() if plaintext_node is not None and plaintext_node.text else ""
            if plaintext:
                subpod_data.append({"text": plaintext})
        if subpod_data:
            pods.append({"title": pod_title, "id": pod_id, "subpods": subpod_data})

    simple_results = [subpod["text"] for pod in pods for subpod in pod["subpods"]]
    return {
        "success": success,
        "error_message": error_message,
        "pods": pods,
        "simple_results": simple_results,
    }


def validate_api_key(app_id):
    """Test API key with a simple query. Returns True if valid, False otherwise."""
    if not app_id or not app_id.strip():
        return False

    raw = _execute_raw_query(app_id.strip(), "1+1")
    if not raw["success"] or raw.get("status") != 200:
        return False

    try:
        parsed = _parse_raw_response(raw["body"])
        return parsed["success"]
    except Exception:
        return False


def query(query_text, app_id, assumptions=None):
    """
    Execute a Wolfram Alpha query.
    
    Args:
        query_text: Question or expression to query
        app_id: Wolfram Alpha API key
        assumptions: List of assumption strings (optional)
    
    Returns:
        {
            "success": bool,
            "message": str,
            "results": {
                "simple": [list of plaintext result strings],
                "detailed": [list of pods with structure]
            }
        }
    """
    if not query_text or not query_text.strip():
        return {
            "success": False,
            "message": "Query cannot be empty.",
            "results": {"simple": [], "detailed": []}
        }
    
    if not app_id or not app_id.strip():
        return {
            "success": False,
            "message": "API key not set. Please log in first.",
            "results": {"simple": [], "detailed": []}
        }

    raw = _execute_raw_query(app_id.strip(), query_text.strip(), assumptions)
    if not raw["success"]:
        error_msg = raw.get("error", "Failed to connect to Wolfram Alpha.")
        if raw.get("status") in (401, 403) or "Invalid appid" in error_msg:
            error_msg = "Invalid API key. Please check and try again."
        return {
            "success": False,
            "message": error_msg,
            "results": {"simple": [], "detailed": []}
        }

    try:
        parsed = _parse_raw_response(raw["body"])
    except ET.ParseError:
        return {
            "success": False,
            "message": "Could not parse Wolfram Alpha response.",
            "results": {"simple": [], "detailed": []}
        }

    if not parsed["success"]:
        return {
            "success": False,
            "message": parsed["error_message"] or "No results found.",
            "results": {"simple": [], "detailed": []}
        }

    if not parsed["simple_results"]:
        return {
            "success": False,
            "message": "Query executed but returned no results.",
            "results": {"simple": [], "detailed": []}
        }

    return {
        "success": True,
        "message": f"Found {len(parsed['simple_results'])} result(s).",
        "results": {
            "simple": parsed["simple_results"],
            "detailed": parsed["pods"]
        }
    }


# ─── Query History ──────────────────────────────────────────────

def _get_history_file():
    """Get path to history JSON file."""
    return Path(__file__).parent / "wolframalpha_history.json"


def get_query_history():
    """Load query history from file. Returns list of dicts."""
    history_file = _get_history_file()
    
    if not history_file.exists():
        return []
    
    try:
        with open(history_file, "r") as f:
            history = json.load(f)
            return history if isinstance(history, list) else []
    except Exception:
        return []


def save_query_to_history(query_text, result_dict):
    """Add query to history, keeping only last 20 entries."""
    history = get_query_history()
    
    # Add new entry at beginning
    history.insert(0, {
        "query": query_text,
        "results": result_dict.get("results", {}),
        "timestamp": str(__import__("datetime").datetime.now())
    })
    
    # Keep only last 20
    history = history[:20]
    
    # Save
    history_file = _get_history_file()
    try:
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass


def clear_history():
    """Delete history file."""
    history_file = _get_history_file()
    try:
        if history_file.exists():
            history_file.unlink()
        return {"success": True, "message": "History cleared."}
    except Exception as e:
        return {"success": False, "message": f"Failed to clear history: {str(e)}"}


# ─── Browser Integration ────────────────────────────────────────

def open_api_portal():
    """Open Wolfram Alpha API portal in default browser."""
    try:
        webbrowser.open("https://developer.wolframalpha.com/access")
        return True
    except Exception:
        return False
