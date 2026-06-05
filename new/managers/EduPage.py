"""EduPage API wrapper — uses the official edupage-api library."""

from datetime import date, timedelta
from edupage_api import Edupage
from edupage_api.exceptions import BadCredentialsException, CaptchaException
import keyring

from config import config_manager
from utilities.logger import get_logger
from utilities.rate_limiter import RateLimiter

# ─── Logging & Configuration ─────────────────────────────────────
logger = get_logger(__name__)
limiter = RateLimiter(calls_per_window=5, window_seconds=60)


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
            logger.debug("Already logged in to EduPage")
            return {"success": True}

        logger.debug(f"Attempting EduPage login for {self.username}@{self.subdomain}")
        try:
            result = self.edupage.login(self.username, self.password, self.subdomain)
            if result is not None:
                logger.warning("EduPage login: 2FA required")
                return {"success": False, "message": "Two-factor auth required. Disable it temporarily."}
            self._logged_in = True

            # Find the student for timetable queries
            students = self.edupage.get_students()
            if students:
                self._student = students[0]
                logger.info(f"EduPage login successful, student: {self._student}")

            return {"success": True}
        except BadCredentialsException:
            logger.warning(f"EduPage login failed: invalid credentials")
            return {"success": False, "message": "Invalid username or password."}
        except CaptchaException:
            logger.warning("EduPage login failed: CAPTCHA required")
            return {"success": False, "message": "CAPTCHA required. Try logging in from a browser first."}
        except Exception as e:
            logger.error(f"EduPage login error: {e}")
            return {"success": False, "message": f"Login error: {e}"}

    def get_grades(self) -> dict:
        """Fetch grades as list of EduGrade objects, grouped by subject."""
        if not self._logged_in:
            r = self.login()
            if not r["success"]:
                return r

        logger.debug("Fetching grades from EduPage")
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

            logger.info(f"Fetched {len(grades)} grades in {len(subjects)} subjects")
            return {
                "success": len(subjects) > 0,
                "subjects": [{"name": k, "grades": v} for k, v in subjects.items()],
                "message": f"Found {len(grades)} grades in {len(subjects)} subjects." if subjects else "No grades found.",
            }
        except Exception as e:
            logger.error(f"Error fetching grades: {e}")
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


class EduPageManager:
    """Manages EduPage session and integrated grade calculation."""

    def __init__(self):
        logger.debug("Initializing EduPageManager")
        self.session = None
        self.manual_grades = {}  # subject -> list of (grade, weight) tuples
        self.remember_creds = False
        self.subdomain = ""
        self.username = ""
        self.password = ""

    def set_credentials(self, subdomain: str, username: str, password: str, remember: bool = False):
        """Set login credentials."""
        logger.debug(f"Setting EduPage credentials for {username}@{subdomain}")
        self.subdomain = subdomain
        self.username = username
        self.password = password
        self.remember_creds = remember

        if remember:
            save_credentials(subdomain, username, password)
            logger.info("EduPage credentials saved to keyring")
        else:
            clear_credentials()
            logger.debug("EduPage credentials cleared from keyring")

    def load_saved_credentials(self):
        """Load saved credentials if available."""
        logger.debug("Loading saved EduPage credentials")
        creds = load_credentials()
        if creds:
            self.subdomain = creds["subdomain"]
            self.username = creds["username"]
            self.password = creds["password"]
            self.remember_creds = True
            logger.info(f"Loaded saved credentials for {creds['username']}")
            return creds
        logger.debug("No saved credentials found")
        return None

    def login(self) -> dict:
        """Login to EduPage."""
        if not self.subdomain or not self.username or not self.password:
            logger.warning("EduPage login attempted with incomplete credentials")
            return {"success": False, "message": "Credentials not set."}

        logger.debug("EduPageManager.login: creating session and logging in")
        self.session = EduSession(self.subdomain, self.username, self.password)
        result = self.session.login()
        if result["success"]:
            result["message"] = "Logged in successfully!"
            logger.info("EduPageManager login successful")
        else:
            logger.warning(f"EduPageManager login failed: {result.get('message', 'unknown error')}")
        return result

    def get_dashboard_data(self) -> dict:
        """Get all dashboard data including integrated grades."""
        logger.debug("get_dashboard_data: fetching all dashboard data")

        # Check rate limit
        allowed, wait = limiter.is_allowed("edupage")
        if not allowed:
            logger.warning(f"Rate limit: dashboard data blocked, wait {wait:.1f}s")
            return {
                "success": False,
                "message": f"Rate limited. Please wait {wait:.0f}s before next request."
            }

        if not self.session:
            logger.debug("No session, attempting login")
            login_result = self.login()
            if not login_result["success"]:
                return login_result

        # Fetch all data
        logger.debug("Fetching: grades, timetable, homework, tests, class_averages, substitutions")
        grades = self.session.get_grades()
        timetable = self.session.get_timetable()
        homework = self.session.get_homework()
        attendance = self.session.get_attendance()
        tests = self.session.get_tests()
        class_avgs = self.session.get_class_averages()
        subs = self.session.get_substitutions()

        # Integrate manual grades with EduPage grades
        integrated_grades = self._integrate_grades(grades)
        logger.info("Dashboard data fetched successfully")

        return {
            "success": True,
            "grades": integrated_grades,
            "timetable": timetable,
            "homework": homework,
            "attendance": attendance,
            "tests": tests,
            "class_averages": class_avgs,
            "substitutions": subs,
            "message": "Dashboard data loaded."
        }

    def _integrate_grades(self, edupage_grades: dict) -> dict:
        """Integrate EduPage grades with manual grades."""
        if not edupage_grades["success"]:
            return edupage_grades

        integrated_subjects = []

        # Start with EduPage subjects
        edupage_subjects = {subj["name"]: subj for subj in edupage_grades["subjects"]}

        # Add manual grades
        for subject, manual_list in self.manual_grades.items():
            if subject in edupage_subjects:
                # Merge with existing EduPage grades
                edupage_subjects[subject]["grades"].extend([
                    {"grade": str(g), "weight": w, "title": "Manual", "date": "", "source": "manual"}
                    for g, w in manual_list
                ])
            else:
                # New subject with only manual grades
                edupage_subjects[subject] = {
                    "name": subject,
                    "grades": [
                        {"grade": str(g), "weight": w, "title": "Manual", "date": "", "source": "manual"}
                        for g, w in manual_list
                    ]
                }

        # Calculate weighted averages for each subject
        for subj_name, subj_data in edupage_subjects.items():
            grades_list = []
            for g in subj_data["grades"]:
                try:
                    grade_val = float(g["grade"])
                    weight = float(g.get("weight", 1))
                    grades_list.append((grade_val, weight))
                except (ValueError, TypeError):
                    continue

            if grades_list:
                avg_result = self.calculate_weighted_average(grades_list)
                subj_data["weighted_average"] = avg_result.get("value", 0)
                subj_data["average_message"] = avg_result["message"]

        integrated_grades = {
            "success": True,
            "subjects": list(edupage_subjects.values()),
            "overall_average": self._calculate_overall_average(edupage_subjects),
            "message": f"Integrated {len(edupage_subjects)} subjects with manual grades."
        }

        return integrated_grades

    def _calculate_overall_average(self, subjects_dict: dict) -> float:
        """Calculate overall weighted average across all subjects."""
        all_grades = []
        for subj_data in subjects_dict.values():
            for g in subj_data["grades"]:
                try:
                    grade_val = float(g["grade"])
                    weight = float(g.get("weight", 1))
                    all_grades.append((grade_val, weight))
                except (ValueError, TypeError):
                    continue

        if not all_grades:
            return 0.0

        result = self.calculate_weighted_average(all_grades)
        return result.get("value", 0.0)

    def add_manual_grade(self, subject: str, grade: int, weight: float) -> dict:
        """Add a manual grade for a subject."""
        if grade < 1 or grade > 5:
            return {"success": False, "message": "Grade must be between 1 and 5."}
        if weight <= 0:
            return {"success": False, "message": "Weight must be positive."}

        if subject not in self.manual_grades:
            self.manual_grades[subject] = []
        self.manual_grades[subject].append((grade, weight))

        return {"success": True, "message": f"Added grade {grade} (weight {weight}) to {subject}."}

    def remove_manual_grade(self, subject: str, index: int) -> dict:
        """Remove a manual grade from a subject."""
        if subject not in self.manual_grades or index >= len(self.manual_grades[subject]):
            return {"success": False, "message": "Grade not found."}

        removed = self.manual_grades[subject].pop(index)
        if not self.manual_grades[subject]:
            del self.manual_grades[subject]

        return {"success": True, "message": f"Removed grade {removed[0]} from {subject}."}

    def get_manual_grades(self) -> dict:
        """Get all manual grades."""
        return {
            "success": True,
            "grades": self.manual_grades,
            "message": f"Manual grades: {sum(len(v) for v in self.manual_grades.values())} entries."
        }

    def calculate_weighted_average(self, grades: list[tuple[int, float]]) -> dict:
        """Calculate weighted average from list of (grade, weight) tuples."""
        if not grades:
            return {"success": False, "message": "No grades entered."}

        total_weighted_sum = sum(grade * weight for grade, weight in grades)
        total_weight = sum(weight for _, weight in grades)

        if total_weight == 0:
            return {"success": False, "message": "Total weight cannot be zero."}

        average = total_weighted_sum / total_weight
        return {"success": True, "value": average, "message": f"Weighted average: {average:.2f}"}

    def calculate_target_grade(self, current_grades: list[tuple[int, float]], target: float) -> dict:
        """Calculate what grade is needed to reach target average."""
        if not current_grades:
            return {"success": False, "message": "Enter at least one grade first."}
        if target < 1 or target > 5:
            return {"success": False, "message": "Target must be between 1 and 5."}

        current_sum = sum(g * w for g, w in current_grades)
        current_weight = sum(w for _, w in current_grades)
        current_avg = current_sum / current_weight

        if current_avg <= target:
            return {
                "success": True,
                "message": f"Current average {current_avg:.2f} is already ≤ {target}. No improvement needed.",
                "needed": None
            }

        # Find required grade with weight 1
        remaining_weight = 1
        needed_grade = (target * (current_weight + remaining_weight) - current_sum) / remaining_weight

        if needed_grade > 5:
            return {
                "success": False,
                "message": f"Impossible to reach {target} with current grades. Maximum possible: {((current_sum + 5 * remaining_weight) / (current_weight + remaining_weight)):.2f}"
            }

        return {
            "success": True,
            "message": f"To reach {target}, you need grade {needed_grade:.1f} with weight {remaining_weight}.",
            "needed": needed_grade,
            "weight": remaining_weight
        }
