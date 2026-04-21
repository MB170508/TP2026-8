"""Lunch menu scraper — fetches daily menus from stravovani.sspbrno.cz."""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def fetch_lunch_menu() -> list[dict]:
    """Fetch the weekly lunch menu, limited to today through next 5 work days."""
    url = "https://stravovani.sspbrno.cz/login"

    try:
        resp = requests.get(url, timeout=10)
    except requests.RequestException as e:
        return [{"date": "Error", "day_name": "Connection failed", "meals": [{"name": "Error", "items": [str(e)]}]}]

    if resp.status_code != 200:
        return [{"date": "Error", "day_name": f"HTTP {resp.status_code}", "meals": [{"name": "Error", "items": ["Failed to load"]}]}]

    soup = BeautifulSoup(resp.text, "lxml")
    dny = soup.find_all("div", {"class": "jidelnicekDen"})

    if not dny:
        return [{"date": "No data", "day_name": "", "meals": [{"name": "", "items": ["No menu data found."]}]}]

    today = datetime.now().date()
    # Calculate cutoff: today + 5 work days ahead
    cutoff = today + timedelta(days=14)  # generous window

    menu = []
    for den in dny:
        # Extract date header
        top_div = den.find("div", class_=lambda c: c and "jidelnicekTop" in c)
        day_text = top_div.get_text(strip=True) if top_div else ""
        # Parse date and day name from text like "Jídelníček na  14.04.2026 - Úterý"
        date_part = ""
        day_name = ""
        if "-" in day_text:
            parts = day_text.split("-", 1)
            date_part = parts[0].replace("Jídelníček na", "").strip()
            day_name = parts[1].strip()
        else:
            date_part = day_text.strip()

        # Parse the date to filter
        try:
            day_date = datetime.strptime(date_part, "%d.%m.%Y").date()
        except ValueError:
            day_date = None

        # Skip past dates and dates too far in the future
        if day_date and (day_date < today or day_date > cutoff):
            continue

        # Extract meals from containers
        meals = []
        containers = den.find_all("div", {"class": "container"})
        for container in containers:
            name_div = container.find("div", class_=lambda c: c and "shrinkedColumn" in c)
            meal_name = name_div.get_text(strip=True) if name_div else ""

            # Food items are in a div with class "column"
            items_div = container.find("div", class_="column")
            items = []
            if items_div:
                raw_text = items_div.get_text(separator=" ", strip=True)
                # Remove allergen info in parentheses like ( 1, 7, 12 )
                import re
                raw_text = re.sub(r'\([^)]*\)', '', raw_text)
                # Split by comma and clean
                parts_raw = [p.strip() for p in raw_text.split(",") if p.strip()]
                for p in parts_raw:
                    cleaned = " ".join(p.split())
                    # Skip drink entries
                    if cleaned and len(cleaned) > 1 and "nápoje" not in cleaned.lower():
                        items.append(cleaned)

            if meal_name or items:
                meals.append({"name": meal_name, "items": items})

        if not meals:
            # Fallback: get all article text
            article = den.find("article")
            if article:
                text = article.get_text(separator="\n", strip=True)
                lines = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 2]
                if lines:
                    meals.append({"name": "", "items": lines})

        menu.append({
            "date": date_part,
            "day_name": day_name,
            "meals": meals,
        })

    # Limit to first 5 days (today + upcoming)
    return menu[:5]


class LunchMenuManager:
    """Lunch menu scraper and manager."""

    def __init__(self):
        self.last_menu = None
        self.last_fetch_time = None

    def fetch_menu(self) -> dict:
        """Fetch the current lunch menu."""
        try:
            menu = fetch_lunch_menu()
            self.last_menu = menu
            self.last_fetch_time = datetime.now()
            return {"success": True, "menu": menu}
        except Exception as e:
            return {"success": False, "message": f"Failed to fetch menu: {str(e)}"}

    def get_cached_menu(self) -> dict:
        """Get the last fetched menu if available."""
        if self.last_menu is None:
            return {"success": False, "message": "No menu cached. Fetch menu first."}
        return {"success": True, "menu": self.last_menu}

    def is_cache_valid(self, max_age_minutes: int = 60) -> bool:
        """Check if cached menu is still valid."""
        if self.last_fetch_time is None:
            return False
        age = datetime.now() - self.last_fetch_time
        return age.total_seconds() < (max_age_minutes * 60)

    def get_menu_summary(self) -> str:
        """Get a text summary of the menu."""
        if not self.last_menu:
            return "No menu available."

        lines = []
        for day in self.last_menu:
            lines.append(f"{day['day_name']} ({day['date']}):")
            for meal in day['meals']:
                if meal['name']:
                    lines.append(f"  {meal['name']}:")
                for item in meal['items']:
                    lines.append(f"    - {item}")
                if not meal['items']:
                    lines.append("    (No items)")
            lines.append("")

        return "\n".join(lines).strip()
