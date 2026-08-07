"""Automated checker for ``Part 3 - Travelling Salesman Problem``.

Run from a terminal with:

    python part3_checker.py

The checker does not modify the original TSP program. It imports the program
as a module, supplies controlled test data, and reports whether each behaviour
passes or fails.
"""

from contextlib import redirect_stdout
from io import StringIO
import importlib.util
import math
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch


PROGRAM_PATH = Path(__file__).with_name("tsp-nearest-neighbour.py")


TEST_DESCRIPTIONS = {
    "test_known_four_city_route": (
        "Algorithm: Known 4-city route and total distance are correct"
    ),
    "test_different_starting_city": (
        "Algorithm: A different starting city produces the expected route"
    ),
    "test_every_city_is_visited_once_before_returning": (
        "Algorithm: Every city is visited once before returning to the start"
    ),
    "test_two_city_minimum_case": (
        "Edge case: The minimum input of two cities works correctly"
    ),
    "test_zero_distance_is_allowed": (
        "Edge case: A valid zero-distance connection is handled correctly"
    ),
    "test_tie_uses_first_city_in_list": (
        "Edge case: Equal distances are resolved consistently"
    ),
    "test_each_step_matches_route_and_matrix": (
        "Algorithm: Journey steps match the route, matrix, and total"
    ),
    "test_integer_rejects_text_and_value_below_minimum": (
        "Validation: Text and integers below the minimum are rejected"
    ),
    "test_city_names_reject_blank_and_case_insensitive_duplicate": (
        "Validation: Blank and duplicate city names are rejected"
    ),
    "test_distance_rejects_text_and_negative_number": (
        "Validation: Non-numeric and negative distances are rejected"
    ),
    "test_distance_matrix_is_symmetric": (
        "Data structure: The distance matrix is symmetric"
    ),
    "test_starting_city_rejects_out_of_range_choices": (
        "Validation: Starting-city choices outside the range are rejected"
    ),
    "test_result_contains_route_steps_and_total": (
        "Output: The route, journey summary, and total are displayed"
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
    """Print one easy-to-read PASS, FAIL, or ERROR line per test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_section = None

    def startTest(self, test):
        super().startTest(test)

        section_by_class = {
            "TestNearestNeighbourAlgorithm": "ALGORITHM AND EDGE-CASE TESTS",
            "TestInputValidation": "INPUT AND DATA-VALIDATION TESTS",
            "TestDisplayedOutput": "DISPLAYED-OUTPUT TEST",
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
        """Show readable diagnostic details without requiring a wrapped stream."""
        for heading, problems in (
            ("FAILED TEST", self.failures),
            ("TEST ERROR", self.errors),
        ):
            for test, traceback_text in problems:
                self.stream.write(f"\n{heading}: {readable_test_name(test)}\n")
                self.stream.write(traceback_text)


def load_tsp_program():
    """Load the hyphenated Python filename without running its main function."""
    if not PROGRAM_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {PROGRAM_PATH.name}. Put this tester in the same "
            "folder as the TSP program."
        )

    specification = importlib.util.spec_from_file_location(
        "tsp_nearest_neighbour",
        PROGRAM_PATH,
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


tsp = load_tsp_program()


class TestNearestNeighbourAlgorithm(unittest.TestCase):
    """Checks the route, journey steps, and total-distance calculations."""

    def setUp(self):
        self.cities = ["A", "B", "C", "D"]
        self.distances = [
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0],
        ]

    def test_known_four_city_route(self):
        route, steps, total = tsp.nearest_neighbour(
            self.cities,
            self.distances,
            starting_city=0,
        )

        self.assertEqual(route, [0, 1, 3, 2, 0])
        self.assertEqual(
            steps,
            [(0, 1, 10), (1, 3, 25), (3, 2, 30), (2, 0, 15)],
        )
        self.assertEqual(total, 80)

    def test_different_starting_city(self):
        route, _, total = tsp.nearest_neighbour(
            self.cities,
            self.distances,
            starting_city=2,
        )

        self.assertEqual(route, [2, 0, 1, 3, 2])
        self.assertEqual(total, 80)

    def test_every_city_is_visited_once_before_returning(self):
        route, _, _ = tsp.nearest_neighbour(
            self.cities,
            self.distances,
            starting_city=0,
        )

        self.assertEqual(route[0], route[-1])
        self.assertEqual(len(route), len(self.cities) + 1)
        self.assertEqual(set(route[:-1]), set(range(len(self.cities))))
        self.assertEqual(len(route[:-1]), len(set(route[:-1])))

    def test_two_city_minimum_case(self):
        cities = ["Kuala Lumpur", "Penang"]
        distances = [[0, 350.5], [350.5, 0]]

        route, steps, total = tsp.nearest_neighbour(cities, distances, 0)

        self.assertEqual(route, [0, 1, 0])
        self.assertEqual(steps, [(0, 1, 350.5), (1, 0, 350.5)])
        self.assertTrue(math.isclose(total, 701.0))

    def test_zero_distance_is_allowed(self):
        cities = ["A", "B", "C"]
        distances = [[0, 0, 5], [0, 0, 2], [5, 2, 0]]

        route, _, total = tsp.nearest_neighbour(cities, distances, 0)

        self.assertEqual(route, [0, 1, 2, 0])
        self.assertEqual(total, 7)

    def test_tie_uses_first_city_in_list(self):
        cities = ["A", "B", "C"]
        distances = [[0, 5, 5], [5, 0, 2], [5, 2, 0]]

        route, _, _ = tsp.nearest_neighbour(cities, distances, 0)

        self.assertEqual(route[1], 1)

    def test_each_step_matches_route_and_matrix(self):
        route, steps, total = tsp.nearest_neighbour(
            self.cities,
            self.distances,
            starting_city=0,
        )

        for index, (from_city, to_city, distance) in enumerate(steps):
            self.assertEqual(from_city, route[index])
            self.assertEqual(to_city, route[index + 1])
            self.assertEqual(distance, self.distances[from_city][to_city])

        self.assertEqual(total, sum(step[2] for step in steps))


class TestInputValidation(unittest.TestCase):
    """Simulates user input to check that invalid values are rejected."""

    def run_silently(self, function, *args):
        output = StringIO()
        with redirect_stdout(output):
            result = function(*args)
        return result, output.getvalue()

    @patch("builtins.input", side_effect=["abc", "1", "4"])
    def test_integer_rejects_text_and_value_below_minimum(self, _mock_input):
        result, output = self.run_silently(tsp.get_integer, "Number: ", 2)

        self.assertEqual(result, 4)
        self.assertIn("whole number", output)
        self.assertIn("greater than or equal to 2", output)

    @patch("builtins.input", side_effect=["", "KL", "kl", "Penang"])
    def test_city_names_reject_blank_and_case_insensitive_duplicate(
        self,
        _mock_input,
    ):
        cities, output = self.run_silently(tsp.get_city_names, 2)

        self.assertEqual(cities, ["KL", "Penang"])
        self.assertIn("cannot be empty", output)
        self.assertIn("already been entered", output)

    @patch("builtins.input", side_effect=["far", "-5", "12.75"])
    def test_distance_rejects_text_and_negative_number(self, _mock_input):
        result, output = self.run_silently(tsp.get_distance, "Distance: ")

        self.assertEqual(result, 12.75)
        self.assertIn("Please enter a number", output)
        self.assertIn("cannot be negative", output)

    @patch("builtins.input", side_effect=["10", "20", "30"])
    def test_distance_matrix_is_symmetric(self, _mock_input):
        matrix, _ = self.run_silently(
            tsp.get_distance_matrix,
            ["A", "B", "C"],
        )

        expected = [[0.0, 10.0, 20.0], [10.0, 0.0, 30.0], [20.0, 30.0, 0.0]]
        self.assertEqual(matrix, expected)

        for row in range(len(matrix)):
            self.assertEqual(matrix[row][row], 0.0)
            for column in range(len(matrix)):
                self.assertEqual(matrix[row][column], matrix[column][row])

    @patch("builtins.input", side_effect=["0", "5", "2"])
    def test_starting_city_rejects_out_of_range_choices(self, _mock_input):
        choice, output = self.run_silently(
            tsp.get_starting_city,
            ["A", "B", "C"],
        )

        self.assertEqual(choice, 1)
        self.assertIn("greater than or equal to 1", output)
        self.assertIn("number from 1 to 3", output)


class TestDisplayedOutput(unittest.TestCase):
    """Checks that important information is shown clearly to the user."""

    def test_result_contains_route_steps_and_total(self):
        cities = ["A", "B"]
        route = [0, 1, 0]
        steps = [(0, 1, 8), (1, 0, 8)]
        output = StringIO()

        with redirect_stdout(output):
            tsp.display_result(cities, route, steps, 16)

        displayed_text = output.getvalue()
        self.assertIn("A -> B -> A", displayed_text)
        self.assertIn("JOURNEY SUMMARY", displayed_text)
        self.assertIn("Total distance:", displayed_text)
        self.assertIn("16", displayed_text)
        self.assertIn("heuristic solution", displayed_text)


if __name__ == "__main__":
    print("=" * 72)
    print("TSP NEAREST NEIGHBOUR - AUTOMATED TEST REPORT")
    print("=" * 72)
    print(f"Program checked : {PROGRAM_PATH.name}")
    print("Tests performed : algorithm, edge cases, validation, and output")
    print("-" * 72)

    test_suite = unittest.TestSuite(
        [
            unittest.defaultTestLoader.loadTestsFromTestCase(
                TestNearestNeighbourAlgorithm
            ),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestInputValidation),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestDisplayedOutput),
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
        print("\n" + "-" * 72)
        print("FAILURE DETAILS")
        print("-" * 72)
        test_result.printErrors()

    failed = len(test_result.failures)
    errors = len(test_result.errors)
    skipped = len(test_result.skipped)
    passed = test_result.testsRun - failed - errors - skipped

    print("\n" + "=" * 72)
    print("FINAL TEST SUMMARY")
    print("=" * 72)
    print(f"Total tests : {test_result.testsRun}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print(f"Errors      : {errors}")
    print(f"Skipped     : {skipped}")
    print(f"Time taken  : {elapsed_time:.3f} seconds")
    print("-" * 72)

    if test_result.wasSuccessful():
        print("OVERALL RESULT: ALL TESTS PASSED - PROGRAM CHECK SUCCESSFUL")
    else:
        print("OVERALL RESULT: SOME TESTS FAILED - REVIEW THE DETAILS ABOVE")

    print("=" * 72)
    sys.exit(0 if test_result.wasSuccessful() else 1)