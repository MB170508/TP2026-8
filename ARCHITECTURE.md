# Architecture Guide

Technical documentation for IT Toolbox development.

## Data Flow

1. **User Input** → Text field, dropdown, or button
2. **Event Handler** → Validates input (real-time on_change)
3. **Manager Class** → Processes data, calls business logic
4. **Business Logic** → Calculation, transformation, API call
5. **Result Dict** → `{"success": bool, "message": str, "data": {...}}`
6. **UI Update** → Display result or error message
7. **Logging** → Logged to file + console

## Error Handling Pattern

All operations return a standard dict:

```python
# Success
{"success": True, "message": "Done", "data": {...}}

# Error
{"success": False, "message": "User-facing error", "error": "error_type"}

# Rate limited
{"success": False, "message": "Rate limited. Wait 45s", "error": "rate_limited"}

# Validation error
{"success": False, "message": "Invalid IPv4 network format"}
```

UI displays `message` to user, logs full response and stack trace.

## State Management

State lives in multiple places:

| Location | Type | Lifetime | Examples |
|----------|------|----------|----------|
| UI controls | Immediate | During tab | TextField values, checkbox states |
| Manager objects | In-memory | App lifetime | Cached grades, quiz state |
| JSON files | Persistent | Until user deletes | Flashcard decks, notes, EduPage creds |
| Config file | Persistent | User edits | API timeouts, rate limits |
| Logs | Append-only | Until user clears | All operations, errors |

## Async Operations

Long-running operations (API calls, I/O) run asynchronously:

```python
def handler(e):
    # Synchronous: Set loading state
    load_button.disabled = True
    status_text.value = "Loading..."
    page.update()
    
    # Asynchronous: Run in thread pool
    asyncio.create_task(handler_async(e))

async def handler_async(e):
    try:
        # Blocking call runs in thread, doesn't freeze UI
        result = await asyncio.to_thread(manager.fetch_data)
        
        # Back on UI thread for updates
        display_result(result)
    except Exception as ex:
        logger.exception("Operation failed")
        status_text.value = f"Error: {str(ex)}"
    finally:
        load_button.disabled = False
        page.update()
```

**Why:** Flet runs on a single thread. Without async, network calls freeze the UI.

**Constraint:** Flet doesn't support native asyncio event loops, so `asyncio.to_thread()` wraps blocking calls.

## Input Validation

Two-layer validation:

1. **Real-time** (on_change) — Shows error as user types, doesn't submit
   - Uses `validators.py` functions
   - Updates error widget immediately
   - Example: `validate_ipv4_network(value)`

2. **Submission** (on_click) — Validates again before processing
   - Re-checks all fields
   - Prevents double-submission
   - Returns early if invalid

```python
def on_input_change(e):
    is_valid, msg = validate_ipv4_network(e.control.value)
    error_widget.value = msg if not is_valid else ""
    page.update()

def on_submit(e):
    if not validate_ipv4_network(network_input.value)[0]:
        error_widget.value = "Invalid network"
        return
    # Process...
```

## Rate Limiting

Sliding window algorithm per API:

```python
limiter = RateLimiter(max_calls=5, time_window=60)

def query(text):
    if not limiter.can_call():  # Checks sliding window
        remaining, reset_in = limiter.get_remaining()
        return {"success": False, "message": f"Rate limited. Wait {reset_in:.0f}s"}
    
    # Make API call...
```

**Window:** 60 seconds  
**Limit:** 5 calls per window per API  
**Storage:** In-memory (resets on app restart)  
**Per-API:** Wolfram, Lunch, EduPage each have independent counters

## Configuration

Singleton config manager loaded at startup:

```python
# config.py
class ConfigManager:
    def __init__(self):
        self.config = self._load_config()
    
    def get(self, key: str, default=None):
        # Dot-separated path: "timeouts.wolfram_seconds"
        return self._nested_get(key, default)

config_manager = ConfigManager()
```

**Usage:**
```python
timeout = config_manager.get("timeouts.wolfram_seconds", 15)
```

**File:** `~/.ittoolbox/config.json`  
**Merge:** User config merges with defaults (user overrides)  
**Reload:** On app restart (not hot-reloadable)

## Logging

Centralized setup in `utilities/logger.py`:

```python
# File handler (DEBUG)
~/.ittoolbox/logs/toolbox.log

# Console handler (WARNING+)
Prints to stderr

# Format
"2026-06-05 14:30:15,123 | INFO | managers.WolframAlpha:query:45 | Successfully queried: 2+2"
```

**Usage:**
```python
from utilities.logger import get_logger
logger = get_logger(__name__)

logger.debug(f"Starting operation with params: {params}")
logger.info("Operation successful")
logger.warning("Using cached result (network unavailable)")
logger.error(f"Operation failed: {error}", exc_info=True)
```

**No password/key logging:** Validators and managers never log sensitive data.

## Components

Reusable UI components in `ui/components.py`:

```python
from ui.components import (
    styled_card,      # Consistent card styling
    error_row,        # Error display with icon
    info_banner,      # Info/warning banner
    result_box,       # Result display
    history_item,     # Query history entry
    spinner_overlay   # Loading indicator
)
```

**Benefit:** Changes to styling update everywhere automatically.

## Input Debouncing

Used for high-frequency events (text input):

```python
from utilities.debounce import Debouncer

predictions_debouncer = Debouncer(delay=0.3)  # 300ms

def on_text_change(e):
    # Debounces: only fires after 300ms of no typing
    predictions_debouncer.call(update_predictions)

def update_predictions():
    preds = notes_manager.get_predictions(note_editor.value)
    # Update UI...
```

**Why:** Prevents lag from running expensive operations on every keystroke.

## Constants

Centralized UI constants in `ui/constants.py`:

```python
from ui.constants import (
    PRIMARY_COLOR,      # Theme primary
    ERROR_COLOR,        # Red for errors
    CARD_BACKGROUND,    # Card styling
    WINDOW_WIDTH,       # Default 1100
    WINDOW_HEIGHT       # Default 850
)
```

**Benefit:** Theme changes update everywhere.

## Validators

Input validation functions in `utilities/validators.py`:

```python
def validate_ipv4_network(value: str) -> Tuple[bool, str]:
    """Validate CIDR notation."""
    if '/' not in value:
        return False, "Use CIDR format: 192.168.0.0/24"
    # ...
    return True, ""
```

**Pattern:** Returns `(is_valid, error_message)`

## Managers

Business logic classes for each tool:

```python
# managers/IPv4Subnetting.py
class SubnetCalculator:
    def add_segment(self, users: str) -> dict:
        """Add segment to calculation."""
        if not users.isdigit():
            return {"success": False, "message": "Must be a number"}
        # ... calculation ...
        return {"success": True, "message": "...", "segments": [...]}
```

**Pattern:** All methods return `{"success": bool, "message": str, ...}` dict

**Logging:** Each method logs entry, exit, and errors

**Rate limiting:** Checked at entry point (before processing)

## Security

### Input Validation

All user input validated before use:
- Network addresses parsed and validated
- Numbers range-checked
- Strings length-limited
- Boolean expressions validated before eval

### Secure Storage

- API keys: Stored in config or system keyring
- Passwords: Never stored (re-entered each login)
- Credentials: Validated on use, logged anonymously

### Logging

- Never log full API responses
- Never log user credentials
- Never log raw user input
- Log only: operation name, result, errors (anonymized)

## Performance

### Caching

- Lunch menu: 24-hour cache  
- Wolfram history: Last 50 queries
- EduPage grades: Session-local cache
- Notes: Auto-saved on change

### Optimization

- Boolean algebra: Max 12 variables (prevents 33M row tables)
- Debouncing: 300ms for predictions (prevents lag)
- Async I/O: Prevents UI freezes on network
- Lazy loading: Managers instantiated on tab open

## Testing

Integration tests in `test_all.py`:

```bash
python test_all.py
# or
python -m pytest tests/
```

**Coverage:**
- Input validation (edge cases, boundaries)
- Manager classes (happy path + error cases)
- Calculation correctness
- File I/O (read/write)

## Deployment

Single Python script: `main.py`

No build step, no compilation needed.

**Requirements:**
- Python 3.8+
- Dependencies: `pip install -r requirements.txt`
- Permissions: Read/write to `~/.ittoolbox/`

## Future Improvements

| Feature | Effort | Value |
|---------|--------|-------|
| Tab extraction (full modularization) | 8h | Medium (code organization) |
| Hot-reload config | 2h | Low (niche use case) |
| Mobile-responsive layout | 12h | Medium (platform expansion) |
| Dark mode customization | 3h | Low (system mode sufficient) |
| Plugin system | 16h | High (extensibility) |
| Real-time collaboration | 20h | Low (local tool focus) |
| Cloud backup | 8h | Medium (data safety) |

## Architecture Decisions

| Decision | Rationale | Alternative Considered |
|----------|-----------|------------------------|
| Thread pool for async | Flet runs single-threaded; async avoids conflicts | Native asyncio (incompatible) |
| Config in `~/.ittoolbox/` | Unix standard; portable; separate from code | In-repo config (not portable) |
| Logging both file + console | File for debugging; console for user feedback | One or the other (incomplete visibility) |
| Singleton config manager | Global access without parameter passing | Dependency injection (more boilerplate) |
| Return dicts for results | Standard across all managers; easy JSON serialization | Exceptions (harder testing), Classes (more complex) |
| Per-API rate limiters | Isolation; independent limits per service | Global limiter (too restrictive) |

## Troubleshooting

### "Module not found" error

Check imports use managers/ prefix:
```python
# ❌ Wrong
from IPv4Subnetting import SubnetCalculator

# ✅ Correct
from managers.IPv4Subnetting import SubnetCalculator
```

### UI freeze on network call

Convert handler to async:
```python
# ❌ Freezes UI
def handler(e):
    result = manager.fetch_data()  # Blocks!

# ✅ Responsive
def handler(e):
    asyncio.create_task(handler_async(e))

async def handler_async(e):
    result = await asyncio.to_thread(manager.fetch_data)
```

### Rate limit false positives

Check wall-clock time, not just call count:
```python
# Rate limiter uses time.time() not call count
# Clocks out of sync can cause issues

# Verify: System time correct?
date  # On Linux
```

### Logs not appearing

Check permissions and directory:
```bash
ls -la ~/.ittoolbox/logs/
# Should be readable/writable

# Verify logging initialized:
python -c "from utilities.logger import init_logging; init_logging(); print('✓')"
```
