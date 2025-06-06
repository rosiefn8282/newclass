import pandas as pd
import random

# زمان‌ها از ساعت 7:30 تا 18 با بازه‌های متنوع
TIME_SLOTS = [
    ("07:30", "09:00"), ("09:15", "10:45"), ("11:00", "12:30"),
    ("13:30", "15:00"), ("15:15", "16:45"), ("17:00", "18:30")
]
DAYS = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه"]

def read_input_data(filename="input_data.xlsx"):
    teachers_df = pd.read_excel(filename, sheet_name="اساتید")
    courses_df = pd.read_excel(filename, sheet_name="دروس")
    rooms_df = pd.read_excel(filename, sheet_name="کلاس‌ها")
    return teachers_df, courses_df, rooms_df

def generate_random_schedule(courses, teachers, rooms):
    schedule = []
    for _, course in courses.iterrows():
        teacher = teachers[teachers["درس"] == course["نام"]].sample(1).iloc[0]
        possible_days = teacher["روزهای آزاد"].split(",")
        room = rooms.sample(1).iloc[0]
        day = random.choice(possible_days)
        time_slot = random.choice(TIME_SLOTS)
        schedule.append({
            "course": course["نام"],
            "teacher": teacher["نام"],
            "day": day,
            "time_slot": time_slot,
            "room": room["نام"]
        })
    return schedule

def has_conflict(schedule):
    seen = set()
    for item in schedule:
        key = (item["day"], item["time_slot"], item["room"])
        if key in seen:
            return True
        seen.add(key)
    return False

def evaluate_schedule(schedule):
    if has_conflict(schedule):
        return 0
    return len(schedule)

def run_genetic_algorithm():
    teachers_df, courses_df, rooms_df = read_input_data()
    best = None
    best_score = -1
    for _ in range(200):
        candidate = generate_random_schedule(courses_df, teachers_df, rooms_df)
        score = evaluate_schedule(candidate)
        if score > best_score:
            best = candidate
            best_score = score
    return best, best_score
# ----- تعریف زمان‌های مجاز -----
def generate_time_slots(start_time, end_time, durations):
    time_slots = []
    base_time = datetime.datetime.strptime(start_time, "%H:%M")
    end_time = datetime.datetime.strptime(end_time, "%H:%M")

    for duration in durations:
        slot_time = base_time
        while slot_time + datetime.timedelta(hours=duration) <= end_time:
            slot_start = slot_time.time()
            slot_end = (slot_time + datetime.timedelta(hours=duration)).time()
            time_slots.append((slot_start, slot_end, duration))
            slot_time += datetime.timedelta(minutes=30)

    return time_slots

time_slots = generate_time_slots("07:30", "18:00", [1.5, 3, 4])
weekdays = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه"]

# ----- تعریف ساختار ژن -----
class Gene:
    def __init__(self, course, teacher, day, time_slot, room):
        self.course = course
        self.teacher = teacher
        self.day = day
        self.time_slot = time_slot
        self.room = room

    def __repr__(self):
        return f"{self.course} | {self.teacher} | {self.day} | {self.time_slot[0]}-{self.time_slot[1]} | کلاس {self.room}"

# ----- خواندن فایل اکسل -----
df_teachers = pd.read_excel("input_data.xlsx", sheet_name="اساتید")
df_courses = pd.read_excel("input_data.xlsx", sheet_name="دروس")
df_rooms = pd.read_excel("input_data.xlsx", sheet_name="کلاس‌ها")

# ----- توابع کمکی -----
def get_teacher_available_days(teacher_name):
    match = df_teachers[df_teachers["نام استاد"] == teacher_name]
    if not match.empty:
        return match.iloc[0]["روزهای آزاد"].replace('،', ',').split(',')
    return []

def has_conflict(g1, g2):
    if g1.day != g2.day:
        return False
    start1, end1 = g1.time_slot[0], g1.time_slot[1]
    start2, end2 = g2.time_slot[0], g2.time_slot[1]
    overlap = max(start1, start2) < min(end1, end2)
    if overlap:
        return g1.teacher == g2.teacher or g1.room == g2.room
    return False

def evaluate_schedule(chromosome):
    score = 100
    for i in range(len(chromosome)):
        for j in range(i + 1, len(chromosome)):
            if has_conflict(chromosome[i], chromosome[j]):
                score -= 30
    for gene in chromosome:
        available_days = get_teacher_available_days(gene.teacher)
        if gene.day not in [d.strip() for d in available_days]:
            score -= 20
    return score
