"""
Problem 1 - Greedy Algorithm: Activity Selection Problem
Scenario: Hall Booking Scheduler for Clubs

Multiple clubs want to book the same venue for one day. Each club
submits a request with a start and end time. However
the venue can only accommodate one club at a time. The result should select 
the maximum number of non-clashing club bookings.
"""


class Activity:

    def __init__(self, name, start, finish):
        self.name = name
        self.start = start
        self.finish = finish

    def __repr__(self):
        return f"{self.name} [{format_time(self.start)} - {format_time(self.finish)}]"


def parse_time(raw):
    parts = raw.split(":")
    if len(parts) != 2:
        return None

    hh_str, mm_str = parts[0].strip(), parts[1].strip()
    if not (hh_str.isdigit() and mm_str.isdigit()):
        return None

    hh, mm = int(hh_str), int(mm_str)
    if not (0 <= hh <= 23 and 0 <= mm <= 59):
        return None

    return hh * 60 + mm


def format_time(minutes):
    """Format minutes-since-midnight back into a 24-hour "HH:MM" string."""
    hh, mm = divmod(minutes, 60)
    return f"{hh:02d}:{mm:02d}"


def format_duration(minutes):
    """Format a duration in minutes as e.g. "1h 30m", "45m" or "2h"."""
    hh, mm = divmod(minutes, 60)
    if hh and mm:
        return f"{hh}h {mm}m"
    if hh:
        return f"{hh}h"
    return f"{mm}m"


#General manual merge sort, activities are sorted in ascending order
def merge_sort(activities, key):
    if len(activities) <= 1:
        return activities[:]

    mid = len(activities) // 2
    left = merge_sort(activities[:mid], key)
    right = merge_sort(activities[mid:], key)
    return _merge(left, right, key)


def _merge(left, right, key):
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def merge_sort_by_finish(activities):
    return merge_sort(activities, key=lambda a: a.finish)


def merge_sort_by_start(activities):
    return merge_sort(activities, key=lambda a: a.start)


#Greedy Algorithm
def select_activities(activities):
    if not activities:
        return [], []

    sorted_activities = merge_sort_by_finish(activities)

    selected = []
    trace = []
    last_finish = None
    last_selected_name = None

    for step, activity in enumerate(sorted_activities, start=1):
        if last_finish is None:
            # The first activity in order of completion time will not overlap with other activities, therefore, it is always the correct starting choice for a greedy algorithm.
            decision = "SELECT"
            reason = "earliest finish time overall - no prior booking to overlap with"
        elif activity.start >= last_finish:
            # Greedy choice: Accept, because it begins/comes later than the end time of the last accepted activity, therefore, there will be no overlap.
            decision = "SELECT"
            reason = (
                f"start {format_time(activity.start)} >= last finish "
                f"{format_time(last_finish)} ({last_selected_name}) - no overlap"
            )
        else:
            decision = "REJECT"
            reason = (
                f"start {format_time(activity.start)} < last finish "
                f"{format_time(last_finish)} ({last_selected_name}) - overlaps"
            )

        trace.append((step, activity, decision, reason))

        if decision == "SELECT":
            selected.append(activity)
            last_finish = activity.finish
            last_selected_name = activity.name

    return selected, trace


def print_activity_table(title, activities):
    print(f"\n{title}")
    if not activities:
        print("  (none)")
        return

    name_width = max(len(a.name) for a in activities)
    name_width = max(name_width, len("Club"))

    header = f"  {'Club'.ljust(name_width)} | {'Start':>5} | {'Finish':>6}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for a in activities:
        print(f"  {a.name.ljust(name_width)} | {format_time(a.start):>5} | {format_time(a.finish):>6}")


def decision_label(decision):
    """Return an eye-catching label for a SELECT/REJECT decision."""
    return ">>> SELECTED" if decision == "SELECT" else ">>> REJECTED"


def print_sorted_by_finish(activities):
    """Show the bookings in the order the greedy algorithm will examine them."""
    print("\nBookings after sorting by finish time:")
    sorted_activities = merge_sort_by_finish(activities)

    name_width = max(len(a.name) for a in sorted_activities)
    name_width = max(name_width, len("Club"))

    for i, a in enumerate(sorted_activities, start=1):
        print(f"  {i}. {a.name.ljust(name_width)}   {format_time(a.start)} - {format_time(a.finish)}")

    print("\nGreedy algorithm starts...")


def print_greedy_trace(trace):
    print("\nGreedy decision trace (examined in order of finish time):")
    if not trace:
        print("  (none)")
        return

    name_width = max(len(a.name) for _, a, _, _ in trace)
    name_width = max(name_width, len("Club"))
    decision_width = len(">>> SELECTED")

    header = (
        f"  {'Stage':>5} | {'Club'.ljust(name_width)} | {'Start':>5} | "
        f"{'Finish':>6} | {'Decision'.ljust(decision_width)} | Reason"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))
    for step, activity, decision, reason in trace:
        label = decision_label(decision)
        print(
            f"  {step:>5} | {activity.name.ljust(name_width)} | {format_time(activity.start):>5} | "
            f"{format_time(activity.finish):>6} | {label.ljust(decision_width)} | {reason}"
        )


def run_interactive_trace(trace):
    """Walk through the greedy decisions one at a time, pausing for Enter."""
    print("\nInteractive step-by-step walkthrough:")
    if not trace:
        print("  (none)")
        return

    for step, activity, decision, reason in trace:
        print(f"\nStep {step}")
        print(f"Current booking:\n  {activity.name} ({format_time(activity.start)} - {format_time(activity.finish)})")
        print(f"Decision:\n  {decision_label(decision)}")
        print(f"Reason:\n  {reason}")
        input("Press Enter to continue...")


def print_final_schedule(selected):
    print("\nFinal Hall Schedule:")
    if not selected:
        print("  (no bookings selected)")
        return
    for a in selected:
        print(f"  {format_time(a.start)} - {format_time(a.finish)}   {a.name}")


def print_statistics(activities, selected):
    accepted = len(selected)
    rejected = len(activities) - accepted
    busy_time = sum(a.finish - a.start for a in selected)

    earliest_start = min(a.start for a in activities)
    latest_finish = max(a.finish for a in activities)
    span = max(latest_finish - earliest_start, 1)
    utilization = busy_time / span * 100

    print("\nStatistics:")
    print(f"  Accepted bookings : {accepted}")
    print(f"  Rejected bookings : {rejected}")
    print(
        f"  Hall utilization  : {utilization:.0f}% "
        f"({format_duration(busy_time)} used out of {format_duration(span)} available)"
    )


# AI-assisted:
# The ASCII timeline visualization was generated
def print_timeline(activities, selected):
    print("\nTimeline (# = selected, . = not selected):")
    if not activities:
        print("  (none)")
        return

    earliest_start = min(a.start for a in activities)
    latest_finish = max(a.finish for a in activities)
    span = max(latest_finish - earliest_start, 1)
    width = min(50, span)
    scale = width / span
    selected_names = {a.name for a in selected}

    name_width = max(len(a.name) for a in activities)
    name_width = max(name_width, len("Club"))

    for a in merge_sort_by_start(activities):
        start_col = round((a.start - earliest_start) * scale)
        end_col = max(round((a.finish - earliest_start) * scale), start_col + 1)
        mark = "#" if a.name in selected_names else "."
        bar = " " * start_col + mark * (end_col - start_col)
        print(f"  {a.name.ljust(name_width)} | {bar}")

    ruler = f"{format_time(earliest_start)}{'.' * max(width - 11, 1)}{format_time(latest_finish)}"
    print(f"  {'time ->'.ljust(name_width)} | {ruler}")


def read_int(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("  Please enter a whole number.")


def read_time(prompt):
    while True:
        raw = input(prompt).strip()
        minutes = parse_time(raw)
        if minutes is not None:
            return minutes
        print("  Please enter a time as HH:MM in 24-hour format (e.g. 08:30, 14:00).")

# Prompt hall booking request and validation
def read_activities_from_user():
    count = read_int("How many clubs want to book the hall? ")
    while count <= 0:
        print("  Please enter a positive number.")
        count = read_int("How many clubs want to book the hall? ")

    activities = []
    for i in range(1, count + 1):
        print(f"\nClub {i}:")
        name = input("  Club name : ").strip()
        if not name:
            name = f"Club{i}"

        while True:
            start = read_time("  Requested start time (HH:MM, 24-hour): ")
            finish = read_time("  Requested finish time (HH:MM, 24-hour): ")
            if finish > start:
                break
            print("  Finish time must be later than start time on the same day. Try again.")

        activities.append(Activity(name, start, finish))

    return activities


def show_schedule(activities):
    selected, trace = select_activities(activities)

    print_activity_table("All booking requests received:", activities)
    print_sorted_by_finish(activities)

    walkthrough = input("\nWalk through the greedy algorithm step-by-step? (Y/N): ").strip().lower()
    if walkthrough == "y":
        run_interactive_trace(trace)
    else:
        print_greedy_trace(trace)

    print_activity_table("Selected bookings (max, non-overlapping):", selected)
    print_final_schedule(selected)
    print_timeline(activities, selected)
    print_statistics(activities, selected)

#CLI Menu
def print_menu():
    print("\n" + "=" * 60)
    print("Hall Booking Scheduler (Activity Selection - Greedy Algorithm)")
    print("=" * 60)
    print("1. Enter booking requests")
    print("2. Exit")


def run():
    print("Each club submits one booking request for the hall.")
    print("Only one club can use the hall at a time.")

    while True:
        print_menu()
        choice = input("Choice: ").strip()

        if choice == "1":
            activities = read_activities_from_user()
            show_schedule(activities)
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("  Please choose 1, or 2 .")


if __name__ == "__main__":
    run()
