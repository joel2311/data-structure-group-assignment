"""Automated checker for ``Part 1 - Greedy Algorithm``.

Run from a terminal with:

    python part1_checker.py

The checker does not modify the original program. It imports the program as a
module, supplies controlled test data, and reports whether each behaviour
passes or fails.
"""

from contextlib import redirect_stdout
from io import StringIO
import importlib.util
from itertools import combinations
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch


PROGRAM_PATH = Path(__file__).with_name("Greedy Algorithm.py")


TEST_DESCRIPTIONS = {
    "test_known_schedule_selects_expected_maximum": (
        "Algorithm: A known schedule produces the expected maximum selection"
    ),
    "test_greedy_count_matches_brute_force_optimum": (
        "Algorithm: Greedy result matches a brute-force maximum for sample data"
    ),
    "test_touching_bookings_do_not_overlap": (
        "Edge case: A booking starting at the previous finish time is accepted"
    ),
    "test_all_overlapping_selects_earliest_finishing_booking": (
        "Edge case: Fully overlapping bookings select the earliest finisher"
    ),
    "test_empty_activity_list": (
        "Edge case: An empty activity list returns empty results"
    ),
    "test_trace_records_each_decision_and_reason": (
        "Trace: Every booking receives a SELECT/REJECT decision and explanation"
    ),
    "test_merge_sort_orders_by_finish_without_changing_original": (
        "Sorting: Manual merge sort orders finish times without changing input"
    ),
    "test_merge_sort_is_stable_for_equal_finish_times": (
        "Sorting: Equal finish times preserve their original order"
    ),
    "test_merge_sort_by_start_orders_chronologically": (
        "Sorting: Activities are ordered correctly by starting time"
    ),
    "test_parse_time_accepts_valid_24_hour_times": (
        "Time handling: Valid 24-hour times are converted to minutes"
    ),
    "test_parse_time_rejects_invalid_values": (
        "Time handling: Invalid time formats and ranges are rejected"
    ),
    "test_time_and_duration_formatting": (
        "Time handling: Times and durations are formatted clearly"
    ),
    "test_read_int_recovers_from_non_integer_input": (
        "Validation: Non-integer input is rejected before accepting a number"
    ),
    "test_read_time_recovers_from_invalid_input": (
        "Validation: Invalid times are rejected before accepting a valid time"
    ),
    "test_activity_entry_validates_count_name_and_time_order": (
        "Validation: Club count, blank name, and finish-time order are handled"
    ),
    "test_activity_table_displays_booking_details": (
        "Output: The activity table displays club names and booking times"
    ),
    "test_greedy_trace_displays_selected_and_rejected_bookings": (
        "Output: The decision trace clearly shows selected and rejected bookings"
    ),
    "test_timeline_and_statistics_display_schedule_summary": (
        "Output: Timeline and statistics summarize the selected schedule"
    ),
    "test_interactive_walkthrough_displays_each_step": (
        "Output: Interactive walkthrough presents every decision step"
    ),
    "test_complete_menu_run_handles_invalid_choice_and_booking": (
        "Integration: Complete menu flow validates a choice and schedules a club"
    ),
}


def readable_test_name(test):
    """Return a plain-English description for a test method."""
    method_name = getattr(test, "_testMethodName", str(test))
    return TEST_DESCRIPTIONS.get(
        method_name,
        method_name.removeprefix("test_").replace("_", " ").capitalize(),
    )


class ClearTestResult(unittest.TextTestResult):
    """Print one easy-to-read PASS, FAIL, ERROR, or SKIP line per test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_section = None

    def startTest(self, test):
        super().startTest(test)

        section_by_class = {
            "TestActivitySelection": "ALGORITHM AND EDGE-CASE TESTS",
            "TestMergeSort": "SORTING TESTS",
            "TestTimeHelpers": "TIME-HANDLING TESTS",
            "TestInputValidation": "INPUT AND DATA-VALIDATION TESTS",
            "TestDisplayedOutput": "DISPLAYED-OUTPUT TESTS",
            "TestCompleteProgramFlow": "COMPLETE PROGRAM-FLOW TEST",
        }
        section = section_by_class.get(test.__class__.__name__, "OTHER TESTS")

        if section != self.current_section:
            self.stream.write(f"\n{section}\n")
            self.current_section = section

    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.write(f"[PASS]  {readable_test_name(test)}\n")

    def addFailure(self, test, error):
        super().addFailure(test, error)
        self.stream.write(f"[FAIL]  {readable_test_name(test)}\n")

    def addError(self, test, error):
        super().addError(test, error)
        self.stream.write(f"[ERROR] {readable_test_name(test)}\n")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.stream.write(f"[SKIP]  {readable_test_name(test)} ({reason})\n")

    def printErrors(self):
        """Show readable diagnostic details without needing a wrapped stream."""
        for heading, problems in (
            ("FAILED TEST", self.failures),
            ("TEST ERROR", self.errors),
        ):
            for test, traceback_text in problems:
                self.stream.write(f"\n{heading}: {readable_test_name(test)}\n")
                self.stream.write(traceback_text)


def load_greedy_program():
    """Load the program filename without running its menu."""
    if not PROGRAM_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {PROGRAM_PATH.name}. Put this tester in the same "
            "folder as the Greedy Algorithm program."
        )

    specification = importlib.util.spec_from_file_location(
        "greedy_algorithm",
        PROGRAM_PATH,
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


greedy = load_greedy_program()


def activity(name, start, finish):
    """Create an Activity using convenient HH:MM strings."""
    return greedy.Activity(name, greedy.parse_time(start), greedy.parse_time(finish))


def maximum_compatible_count(activities):
    """Return the maximum valid schedule size by brute force for comparison."""
    best = 0
    for size in range(len(activities) + 1):
        for subset in combinations(activities, size):
            ordered = sorted(subset, key=lambda item: item.start)
            compatible = all(
                ordered[index].start >= ordered[index - 1].finish
                for index in range(1, len(ordered))
            )
            if compatible:
                best = max(best, size)
    return best


class TestActivitySelection(unittest.TestCase):
    """Checks greedy selection, optimality, trace data, and edge cases."""

    def test_known_schedule_selects_expected_maximum(self):
        activities = [
            activity("Robotics", "09:00", "10:00"),
            activity("Debate", "09:30", "11:00"),
            activity("Music", "10:00", "11:00"),
            activity("Chess", "11:00", "12:00"),
            activity("Drama", "11:30", "13:00"),
        ]

        selected, _ = greedy.select_activities(activities)

        self.assertEqual([item.name for item in selected], ["Robotics", "Music", "Chess"])
        self.assertEqual(len(selected), 3)

    def test_greedy_count_matches_brute_force_optimum(self):
        activities = [
            activity("A", "08:00", "09:30"),
            activity("B", "08:30", "10:00"),
            activity("C", "09:30", "10:30"),
            activity("D", "10:00", "12:00"),
            activity("E", "10:30", "11:30"),
            activity("F", "11:30", "13:00"),
            activity("G", "12:00", "14:00"),
        ]

        selected, _ = greedy.select_activities(activities)

        self.assertEqual(len(selected), maximum_compatible_count(activities))
        self.assertEqual([item.name for item in selected], ["A", "C", "E", "F"])

    def test_touching_bookings_do_not_overlap(self):
        activities = [
            activity("A", "09:00", "10:00"),
            activity("B", "10:00", "11:00"),
            activity("C", "11:00", "12:00"),
        ]

        selected, _ = greedy.select_activities(activities)

        self.assertEqual([item.name for item in selected], ["A", "B", "C"])

    def test_all_overlapping_selects_earliest_finishing_booking(self):
        activities = [
            activity("Long", "08:00", "13:00"),
            activity("Middle", "09:00", "12:00"),
            activity("Early", "10:00", "11:00"),
        ]

        selected, _ = greedy.select_activities(activities)

        self.assertEqual([item.name for item in selected], ["Early"])

    def test_empty_activity_list(self):
        selected, trace = greedy.select_activities([])

        self.assertEqual(selected, [])
        self.assertEqual(trace, [])

    def test_trace_records_each_decision_and_reason(self):
        activities = [
            activity("A", "09:00", "10:00"),
            activity("B", "09:30", "10:30"),
            activity("C", "10:00", "11:00"),
        ]

        _, trace = greedy.select_activities(activities)

        self.assertEqual(len(trace), len(activities))
        self.assertEqual([row[0] for row in trace], [1, 2, 3])
        self.assertEqual([row[2] for row in trace], ["SELECT", "REJECT", "SELECT"])
        self.assertIn("earliest finish time", trace[0][3])
        self.assertIn("overlaps", trace[1][3])
        self.assertIn("no overlap", trace[2][3])


class TestMergeSort(unittest.TestCase):
    """Checks the program's manually implemented merge sort."""

    def test_merge_sort_orders_by_finish_without_changing_original(self):
        activities = [
            activity("Late", "11:00", "13:00"),
            activity("Early", "08:00", "09:00"),
            activity("Middle", "09:00", "11:00"),
        ]
        original_order = activities[:]

        sorted_activities = greedy.merge_sort_by_finish(activities)

        self.assertEqual([item.name for item in sorted_activities], ["Early", "Middle", "Late"])
        self.assertEqual(activities, original_order)
        self.assertIsNot(sorted_activities, activities)

    def test_merge_sort_is_stable_for_equal_finish_times(self):
        activities = [
            activity("First", "08:00", "10:00"),
            activity("Second", "09:00", "10:00"),
            activity("Earlier", "07:00", "09:00"),
        ]

        sorted_activities = greedy.merge_sort_by_finish(activities)

        self.assertEqual([item.name for item in sorted_activities], ["Earlier", "First", "Second"])

    def test_merge_sort_by_start_orders_chronologically(self):
        activities = [
            activity("C", "12:00", "13:00"),
            activity("A", "08:00", "10:00"),
            activity("B", "10:00", "11:00"),
        ]

        sorted_activities = greedy.merge_sort_by_start(activities)

        self.assertEqual([item.name for item in sorted_activities], ["A", "B", "C"])


class TestTimeHelpers(unittest.TestCase):
    """Checks time parsing, range validation, and display formatting."""

    def test_parse_time_accepts_valid_24_hour_times(self):
        self.assertEqual(greedy.parse_time("00:00"), 0)
        self.assertEqual(greedy.parse_time(" 09 : 30 "), 570)
        self.assertEqual(greedy.parse_time("23:59"), 1439)

    def test_parse_time_rejects_invalid_values(self):
        invalid_values = ["9", "09:30:00", "ab:cd", "24:00", "12:60", "-1:00", ""]

        for value in invalid_values:
            with self.subTest(value=value):
                self.assertIsNone(greedy.parse_time(value))

    def test_time_and_duration_formatting(self):
        self.assertEqual(greedy.format_time(570), "09:30")
        self.assertEqual(greedy.format_duration(45), "45m")
        self.assertEqual(greedy.format_duration(120), "2h")
        self.assertEqual(greedy.format_duration(150), "2h 30m")


class TestInputValidation(unittest.TestCase):
    """Simulates keyboard input to confirm incorrect values are rejected."""

    @patch("builtins.input", side_effect=["hello", "4"])
    def test_read_int_recovers_from_non_integer_input(self, _mock_input):
        output = StringIO()

        with redirect_stdout(output):
            result = greedy.read_int("Number: ")

        self.assertEqual(result, 4)
        self.assertIn("whole number", output.getvalue())

    @patch("builtins.input", side_effect=["25:00", "nine", "09:15"])
    def test_read_time_recovers_from_invalid_input(self, _mock_input):
        output = StringIO()

        with redirect_stdout(output):
            result = greedy.read_time("Time: ")

        self.assertEqual(result, 555)
        self.assertEqual(output.getvalue().count("HH:MM"), 2)

    @patch(
        "builtins.input",
        side_effect=["abc", "0", "1", "", "09:00", "08:00", "10:00", "11:00"],
    )
    def test_activity_entry_validates_count_name_and_time_order(self, _mock_input):
        output = StringIO()

        with redirect_stdout(output):
            activities = greedy.read_activities_from_user()

        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0].name, "Club1")
        self.assertEqual((activities[0].start, activities[0].finish), (600, 660))
        displayed_text = output.getvalue()
        self.assertIn("whole number", displayed_text)
        self.assertIn("positive number", displayed_text)
        self.assertIn("Finish time must be later", displayed_text)


class TestDisplayedOutput(unittest.TestCase):
    """Checks the tables, trace, timeline, statistics, and walkthrough."""

    def setUp(self):
        self.activities = [
            activity("Robotics", "09:00", "10:00"),
            activity("Debate", "09:30", "11:00"),
            activity("Music", "10:00", "11:00"),
        ]
        self.selected, self.trace = greedy.select_activities(self.activities)

    def test_activity_table_displays_booking_details(self):
        output = StringIO()

        with redirect_stdout(output):
            greedy.print_activity_table("Booking Test", self.activities)

        displayed_text = output.getvalue()
        self.assertIn("Booking Test", displayed_text)
        self.assertIn("Club", displayed_text)
        self.assertIn("Robotics", displayed_text)
        self.assertIn("09:00", displayed_text)
        self.assertIn("11:00", displayed_text)

    def test_greedy_trace_displays_selected_and_rejected_bookings(self):
        output = StringIO()

        with redirect_stdout(output):
            greedy.print_greedy_trace(self.trace)

        displayed_text = output.getvalue()
        self.assertIn("Greedy decision trace", displayed_text)
        self.assertIn(">>> SELECTED", displayed_text)
        self.assertIn(">>> REJECTED", displayed_text)
        self.assertIn("no overlap", displayed_text)
        self.assertIn("overlaps", displayed_text)

    def test_timeline_and_statistics_display_schedule_summary(self):
        output = StringIO()

        with redirect_stdout(output):
            greedy.print_timeline(self.activities, self.selected)
            greedy.print_statistics(self.activities, self.selected)

        displayed_text = output.getvalue()
        self.assertIn("Timeline (# = selected, . = not selected)", displayed_text)
        self.assertIn("Robotics", displayed_text)
        self.assertIn("#", displayed_text)
        self.assertIn(".", displayed_text)
        self.assertIn("Statistics", displayed_text)
        self.assertIn("Accepted bookings : 2", displayed_text)
        self.assertIn("Rejected bookings : 1", displayed_text)
        self.assertIn("Hall utilization", displayed_text)

    @patch("builtins.input", side_effect=["", "", ""])
    def test_interactive_walkthrough_displays_each_step(self, mock_input):
        output = StringIO()

        with redirect_stdout(output):
            greedy.run_interactive_trace(self.trace)

        displayed_text = output.getvalue()
        self.assertEqual(mock_input.call_count, 3)
        self.assertIn("Interactive step-by-step walkthrough", displayed_text)
        self.assertIn("Step 1", displayed_text)
        self.assertIn("Step 3", displayed_text)
        self.assertIn("Decision", displayed_text)
        self.assertIn("Reason", displayed_text)


class TestCompleteProgramFlow(unittest.TestCase):
    """Runs the menu and one booking case with simulated keyboard input."""

    @patch(
        "builtins.input",
        side_effect=["invalid", "1", "1", "Chess Club", "09:00", "10:30", "n", "2"],
    )
    def test_complete_menu_run_handles_invalid_choice_and_booking(self, _mock_input):
        output = StringIO()

        with redirect_stdout(output):
            greedy.run()

        displayed_text = output.getvalue()
        self.assertIn("Hall Booking Scheduler", displayed_text)
        self.assertIn("Please choose 1, or 2", displayed_text)
        self.assertIn("All booking requests received", displayed_text)
        self.assertIn("Chess Club", displayed_text)
        self.assertIn("Selected bookings (max, non-overlapping)", displayed_text)
        self.assertIn("Accepted bookings : 1", displayed_text)
        self.assertIn("Goodbye!", displayed_text)


if __name__ == "__main__":
    print("=" * 76)
    print("GREEDY ACTIVITY SELECTION - AUTOMATED TEST REPORT")
    print("=" * 76)
    print(f"Program checked : {PROGRAM_PATH.name}")
    print("Tests performed : algorithm, sorting, validation, interface, and output")
    print("-" * 76)

    test_suite = unittest.TestSuite(
        [
            unittest.defaultTestLoader.loadTestsFromTestCase(TestActivitySelection),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestMergeSort),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestTimeHelpers),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestInputValidation),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestDisplayedOutput),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestCompleteProgramFlow),
        ]
    )
    test_result = ClearTestResult(
        stream=sys.stdout,
        descriptions=True,
        verbosity=0,
    )

    start_time = time.perf_counter()
    test_suite.run(test_result)
    elapsed_time = time.perf_counter() - start_time

    if test_result.failures or test_result.errors:
        print("\n" + "-" * 76)
        print("FAILURE DETAILS")
        print("-" * 76)
        test_result.printErrors()

    failed = len(test_result.failures)
    errors = len(test_result.errors)
    skipped = len(test_result.skipped)
    passed = test_result.testsRun - failed - errors - skipped

    print("\n" + "=" * 76)
    print("FINAL TEST SUMMARY")
    print("=" * 76)
    print(f"Total tests : {test_result.testsRun}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print(f"Errors      : {errors}")
    print(f"Skipped     : {skipped}")
    print(f"Time taken  : {elapsed_time:.3f} seconds")
    print("-" * 76)

    if test_result.wasSuccessful():
        print("OVERALL RESULT: ALL TESTS PASSED - PROGRAM CHECK SUCCESSFUL")
    else:
        print("OVERALL RESULT: SOME TESTS FAILED - REVIEW THE DETAILS ABOVE")

    print("=" * 76)
    sys.exit(0 if test_result.wasSuccessful() else 1)