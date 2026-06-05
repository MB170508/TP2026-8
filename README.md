# IT Toolbox — Educational Application

Educational calculator and utilities application built with Python and Flet for learning and productivity.

## Features

- **IPv4 Subnetting** — VLSM subnet calculator with custom segment support
- **Multi-Base Calculator** — Binary, octal, decimal, hexadecimal conversions and expressions
- **Boolean Algebra** — Expression simplifier with truth tables (max 12 variables)
- **Unit Converter** — Length, mass, volume, temperature conversions
- **Scientific Calculator** — Trigonometric, logarithmic, and exponential functions
- **Flashcards** — Study system with quiz mode and deck management
- **Notes** — Notepad with CZ/EN word prediction
- **Lunch Menu** — School lunch menu scraper with caching
- **EduPage Integration** — Grade calculator and dashboard access
- **Wolfram Alpha** — Query integration for advanced calculations

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running

```bash
python main.py
```

The application opens in a desktop window. All features work offline except Lunch and Wolfram Alpha, which require network access.

## Configuration

Edit `~/.ittoolbox/config.json` to customize:
- Network timeouts (API calls)
- Cache TTL (lunch menu, Wolfram history)
- Input limits (Boolean algebra variables)
- UI settings (window size, theme)
- Feature flags (enable/disable tools)

**Default config locations:**
- Config: `~/.ittoolbox/config.json`
- Logs: `~/.ittoolbox/logs/toolbox.log`
- Cache: `~/.ittoolbox/` (decks, notes, etc.)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+L` | Load lunch menu |
| `Ctrl+N` | Create new note |
| `Ctrl+Q` | New Wolfram query |
| `Ctrl+D` | New flashcard deck |
| `Escape` | Clear current tab |

## Architecture

```
UI Layer (Flet)         ← Ten tabs, each with event handlers
    ↓
Manager Layer           ← Business logic (SubnetCalculator, etc.)
    ↓
Utilities               ← Validation, logging, rate limiting, async
    ↓
Data Layer              ← JSON files, APIs, external services
```

### Directory Structure

```
ui/
├── main.py              # Entry point orchestrator (150 lines)
├── constants.py         # Colors, sizes, fonts
├── helpers.py          # btn(), section(), sub(), set_error()
├── components.py       # Reusable UI components
└── tabs/
    └── *.py            # Individual tab modules (future)

managers/               # Business logic modules
├── IPv4Subnetting.py
├── BooleanAlgebra.py
├── WolframAlpha.py
├── Lunch.py
├── EduPage.py
└── ...

utilities/              # Shared utilities
├── validators.py       # Input validation functions
├── logger.py          # Centralized logging
├── rate_limiter.py    # API rate limiting
├── async_helpers.py   # Async/thread pool utilities
└── debounce.py        # Input debouncing

tests/
└── test_all.py        # Integration test suite

config.py              # Configuration manager (singleton)
main.py               # Entry point wrapper
requirements.txt      # Python dependencies
```

## Error Handling

All operations return a standard result dict:

```python
{
    "success": True/False,
    "message": "User-facing message",
    # Optional additional fields
    "data": {...}
}
```

Errors are logged to `~/.ittoolbox/logs/toolbox.log` (DEBUG level) and displayed to user (WARNING+ to console).

## Rate Limiting

API calls are rate-limited to prevent quota exhaustion:
- **Wolfram Alpha**: 5 queries/minute
- **EduPage**: 30 requests/minute
- **Lunch Menu**: 1 fetch/hour (cached 24h)

Hitting the limit returns: `"Rate limited. Wait X.Xs"`

## Performance

- Boolean algebra capped at 12 variables (4,096 truth table rows)
- Text predictions debounced 300ms (notes tab)
- Lunch menu cached 24 hours
- Wolfram history limited to 50 items
- Async I/O prevents UI freezes on network calls

## Security

- API keys stored in config or keyring (never logged)
- User input validated before processing
- No sensitive data logged
- EduPage credentials stored securely
- Math eval() sandboxed and validated

## Logging

### Log Levels
- **DEBUG** — Detailed operation traces
- **INFO** — Successful operations
- **WARNING** — Degraded performance (cache fallback, rate limits)
- **ERROR** — Operation failures (with stack traces)

### Log File

Location: `~/.ittoolbox/logs/toolbox.log`

Format: `TIMESTAMP | LEVEL | MODULE:FUNCTION:LINE | MESSAGE`

View last 50 entries:
```bash
tail -50 ~/.ittoolbox/logs/toolbox.log
```

## Development

### Adding a New Tool

1. Create manager class in `managers/new_tool.py`
2. Create tab module in `ui/tabs/new_tool_tab.py`  
3. Add tab label to `ui/main.py` TabBar
4. Add import to `ui/main.py`

### Running Tests

```bash
python -m pytest tests/
# or
python test_all.py
```

## Troubleshooting

**"Rate limited" error**
- Wait 60 seconds before next API query
- Adjust rate limit in `~/.ittoolbox/config.json`

**"Query timed out" error**
- Network is slow; increase timeout in config
- Check internet connection
- Verify API endpoint is accessible

**UI freeze on Lunch or Wolfram**
- Network call is blocking (async conversion needed)
- Check logs: `tail -20 ~/.ittoolbox/logs/toolbox.log`
- Increase timeout if network is slow

**Notes/Decks not saving**
- Check write permissions: `~/.ittoolbox/` must be writable
- Verify disk space available

## Known Limitations

- No concurrent access protection (don't open 2 windows)
- EduPage requires compatible server (`edupage-api` must work)
- Wolfram Alpha requires free API key
- Boolean algebra limited to 12 variables
- No cloud sync or backup

## Dependencies

See `requirements.txt`:
- `flet` — GUI framework
- `requests` — HTTP library
- `beautifulsoup4` — HTML parsing
- `sympy` — Symbolic math
- `edupage-api` — EduPage integration
- `keyring` — Secure credential storage

## License

Educational use only. Not for commercial purposes.

## Support

For issues, check:
1. Logs: `~/.ittoolbox/logs/toolbox.log`
2. Config: `~/.ittoolbox/config.json` (verify syntax)
3. Dependencies: `pip install -r requirements.txt`

For bugs, create an issue with:
- Python version (`python --version`)
- OS (Linux, macOS, Windows)
- Last 20 lines of log file
- Steps to reproduce
