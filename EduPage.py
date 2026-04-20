"""EduPage API wrapper — uses the official edupage-api library."""

from datetime import date, timedelta
from edupage_api import Edupage
from edupage_api.exceptions import BadCredentialsException, CaptchaException
import keyring


def save_credentials(subdomain: str, username: str, password: str) -> bool:
    """Save credentials to keyring if available."""
    try:
        keyring.set_password("edupage", "subdomain", subdomain)
        keyring.set_password("edupage", "username", username)
        keyring.set_password("edupage", "password", password)
        return True
    except Exception:
        return False


def load_credentials() -> dict | None:
    """Load credentials from keyring if available."""
    try:
        subdomain = keyring.get_password("edupage", "subdomain")
        username = keyring.get_password("edupage", "username")
        password = keyring.get_password("edupage", "password")
        if subdomain and username and password:
            return {"subdomain": subdomain, "username": username, "password": password}
        return None
    except Exception:
        return None


def clear_credentials() -> bool:
    """Clear credentials from keyring."""
    try:
        keyring.delete_password("edupage", "subdomain")
        keyring.delete_password("edupage", "username")
        keyring.delete_password("edupage", "password")
        return True
    except Exception:
        return False


class EduSession:
    """Wraps the official edupage-api library for easy access."""

    def __init__(self, subdomain: str, username: str, password: str):
        self.subdomain = subdomain
        self.username = username
        self.password = password
        self.edupage = Edupage()
        self._logged_in = False
        self._student = None

    def login(self) -> dict:
        """Authenticate and return status dict."""
        if self._logged_in:
            return {"success": True}

        try:
            result = self.edupage.login(self.username, self.password, self.subdomain)
            if result is not None:
                return {"success": False, "message": "Two-factor auth required. Disable it temporarily."}
            self._logged_in = True

            # Find the student for timetable queries
            students = self.edupage.get_students()
            if students:
                self._student = students[0]

            return {"success": True}
        except BadCredentialsException:
            return {"success": False, "message": "Invalid username or password."}
        except CaptchaException:
            return {"success": False, "message": "CAPTCHA required. Try logging in from a browser first."}
        except Exception as e:
            return {"success": False, "message": f"Login error: {e}"}

    def get_grades(self) -> dict:
        """Fetch grades as list of EduGrade objects, grouped by subject."""
        if not self._logged_in:
            r = self.login()
            if not r["success"]:
                return r

        try:
            grades = self.edupage.get_grades()
            subjects = {}
            for g in grades:
                subj = g.subject_name or "Unknown"
                if subj not in subjects:
                    subjects[subj] = []
                subjects[subj].append({
                    "grade": g.grade_n if g.grade_n is not None else "",
                    "date": g.date.strftime("%Y-%m-%d") if g.date else "",
                    "weight": g.importance,
                    "title": g.title or "",
                    "comment": g.comment or "",
                    "max_points": g.max_points,
                    "percent": g.percent if g.percent is not None else None,
                    "class_avg": g.class_grade_avg,
                })

            return {
                "success": len(subjects) > 0,
                "subjects": [{"name": k, "grades": v} for k, v in subjects.items()],
                "message": f"Found {len(grades)} grades in {len(subjects)} subjects." if subjects else "No grades found.",
            }
        except Exception as e:
            return {"success": False, "message": f"Error fetching grades: {e}"}

    def get_timetable(self, week_offset: int = 0) -> dict:
        """Fetch timetable for a specific week."""
        if not self._logged_in:
            r = self.login()
            if not r["success"]:
                return r

        if self._student is None:
            return {"success": False, "message": "No student found on this account."}

        try:
            monday = date.today() + timedelta(weeks=week_offset)
            monday = monday - timedelta(days=monday.weekday())

            days = []
            for day_offset in range(5):  # Mon-Fri
                day = monday + timedelta(days=day_offset)
                timetable = self.edupage.get_my_timetable(day)
                if timetable and timetable.lessons:
                    day_lessons = []
                    for lesson in timetable.lessons:
                        if lesson.is_event:
                            continue
                        day_lessons.append({
                            "hour": lesson.period,
                            "subject": lesson.subject.name if lesson.subject else "",
                            "teacher": ", ".join([t.name for t in lesson.teachers]) if lesson.teachers else "",
                            "room": ", ".join([r.name for r in lesson.classrooms]) if lesson.classrooms else "",
                            "start": lesson.start_time.strftime("%H:%M") if lesson.start_time else "",
                            "end": lesson.end_time.strftime("%H:%M") if lesson.end_time else "",
                            "cancelled": lesson.is_cancelled,
                        })
                    if day_lessons:
                        days.append({"date": day.strftime("%Y-%m-%d"), "lessons": day_lessons})

            return {
                "success": len(days) > 0,
                "days": days,
                "message": f"Found {len(days)} days in timetable." if days else "No timetable found for this week.",
            }
        except Exception as e:
            return {"success": False, "message": f"Error fetching timetable: {e}"}

    def get_homework(self) -> dict:
        """Fetch homework from timeline/notifications."""
        if not self._logged_in:
            r = self.login()
            if not r["success"]:
                return r

        try:
            notifications = self.edupage.get_notifications()
            homework = []
            for event in notifications:
                title = getattr(event, "title", "") or ""
                if any(kw in title.lower() for kw in ["homework", "hw", "domáca", "domácí", "úkol", "ukol", "písemka", "písomka"]):
                    homework.append({
                        "subject": getattr(event, "subject", "") or "",
                        "title": title,
                        "due": getattr(event, "date", "") or "",
                        "completed": False,
                        "teacher": getattr(event, "author", "") or "",
                    })

            return {
                "success": len(homework) > 0,
                "assignments": homework,
                "message": f"Found {len(homework)} homework items." if homework else "No homework found.",
            }
        except Exception as e:
            return {"success": False, "message": f"Error fetching homework: {e}"}

    def get_attendance(self) -> dict:
        """Fetch attendance — not directly available via the library."""
        return {"success": False, "records": [], "summary": {}, "message": "Attendance data not available through the API."}

    def get_tests(self) -> dict:
        """Fetch upcoming tests from notifications."""
        if not self._logged_in:
            r = self.login()
            if not r["success"]:
                return r

        try:
            notifications = self.edupage.get_notifications()
            tests = []
            for event in notifications:
                title = getattr(event, "title", "") or ""
                if any(kw in title.lower() for kw in ["test", "písomka", "písemka", "skúška", "zkouška", "exam"]):
                    tests.append({
                        "subject": getattr(event, "subject", "") or "",
                        "title": title,
                        "date": str(getattr(event, "date", "")) if hasattr(event, "date") else "",
                        "type": "Test",
                        "teacher": getattr(event, "author", "") or "",
                        "topics": getattr(event, "note", "") or "",
                    })

            return {
                "success": len(tests) > 0,
                "tests": tests,
                "message": f"Found {len(tests)} upcoming tests." if tests else "No upcoming tests found.",
            }
        except Exception as e:
            return {"success": False, "message": f"Error fetching tests: {e}"}

    def get_class_averages(self) -> dict:
        """Get class averages from grades data."""
        if not self._logged_in:
            r = self.login()
            if not r["success"]:
                return r

        try:
            grades = self.edupage.get_grades()
            averages = {}
            for g in grades:
                if g.class_grade_avg is not None and g.subject_name:
                    subj = g.subject_name
                    if subj not in averages or g.date > averages[subj]["date"]:
                        averages[subj] = {"avg": g.class_grade_avg, "date": g.date}

            result = {k: v["avg"] for k, v in averages.items()}
            return {
                "success": len(result) > 0,
                "averages": result,
                "message": f"Found {len(result)} class averages." if result else "No class averages available.",
            }
        except Exception as e:
            return {"success": False, "message": f"Error fetching class averages: {e}"}

    def get_substitutions(self) -> dict:
        """Get timetable changes/substitutions for the user's class only."""
        if not self._logged_in:
            r = self.login()
            if not r["success"]:
                return r

        try:
            import datetime
            check_date = date.today()
            now = datetime.datetime.now().time()

            # Try to get today's timetable to check if classes are still ongoing
            try:
                today_tt = self.edupage.get_my_timetable(check_date)
                if today_tt and today_tt.lessons:
                    last_lesson_end = max((l.end_time for l in today_tt.lessons), default=None)
                    if last_lesson_end and now > last_lesson_end:
                        # School day is over, check next day
                        check_date += timedelta(days=1)
                        # Skip weekends
                        while check_date.weekday() >= 5:
                            check_date += timedelta(days=1)
            except Exception:
                pass

            # Get user's class info for filtering
            user_class_id = None
            user_class_short = None
            if self._student:
                user_class_id = self._student.class_id
                # Get all classes to find the one matching user's class_id
                
                try:
                    classes = self.edupage.get_classes()
                    for clss in classes:
                        if clss.class_id == user_class_id:
                            user_class_short = clss.short
                            break
                except Exception:
                    pass

            changes = self.edupage.get_timetable_changes(check_date)
            subs = []
            for change in changes:
                change_class = getattr(change, "change_class", "") or ""
                # Filter to only show substitutions for the user's class
                if user_class_short and user_class_short not in str(change_class):
                    continue
                # Also check by class_id if class name doesn't match
                if user_class_id and user_class_short is None:
                    if str(user_class_id) not in str(change_class):
                        continue

                subs.append({
                    "date": str(check_date),
                    "hour": getattr(change, "lesson_n", ""),
                    "title": getattr(change, "title", "") or "",
                    "action": str(getattr(change, "action", "")),
                    "class": change_class,
                })

            return {
                "success": len(subs) > 0,
                "substitutions": subs,
                "message": f"Found {len(subs)} substitutions for {check_date}." if subs else f"No substitutions for {check_date}.",
            }
        except Exception as e:
            return {"success": False, "message": f"Error fetching substitutions: {e}"}
