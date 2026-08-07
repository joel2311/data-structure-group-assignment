"""Automated checker for Part 2: Dynamic Programming.

Run from a terminal with:

    python part2_checker.py

The checker does not modify the original program. It imports the program as a
module, supplies controlled test data, and reports whether each behaviour
passes or fails.
"""

from contextlib import redirect_stdout
from io import StringIO
import importlib.util
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch


PROGRAM_PATH = Path(__file__).with_name("Dynamic Programming.py")


TEST_DESCRIPTIONS = {
    "test_non_greedy_case_finds_optimal_solution": (
        "Algorithm: Dynamic programming finds the optimal non-greedy solution"
    ),
    "test_impossible_target_returns_none": (
        "Edge case: An impossible target is identified correctly"
    ),
    "test_target_smaller_than_every_coin": (
        "Edge case: A target smaller than every coin cannot be formed"
    ),
    "test_single_denomination_reachable_target": (
        "Edge case: A single denomination forms a reachable target correctly"
    ),
    "test_selected_coins_match_target_and_minimum_count": (
        "Algorithm: Selected coins sum to the target and match the DP minimum"
    ),
    "test_dp_values_for_known_example": (
        "Data structure: The DP array contains the expected minimum counts"
    ),
    "test_larger_target_uses_minimum_number_of_coins": (
        "Algorithm: A larger target uses the minimum number of coins"
    ),
    "test_positive_integer_rejects_text_zero_and_negative": (
        "Validation: Text, zero, and negative target values are rejected"
    ),
    "test_denominations_reject_empty_text_and_nonpositive_values": (
        "Validation: Empty, non-numeric, zero, and negative coins are rejected"
    ),
    "test_denominations_remove_duplicates_and_sort": (
        "Validation: Duplicate denominations are removed and values are sorted"
    ),
    "test_coin_count_breakdown": (
        "Supporting function: Selected coins are counted correctly"
    ),
    "test_input_summary_contains_coins_and_target": (
        "Output: The input summary displays the denominations and target"
    ),
    "test_dp_table_marks_unreachable_amounts": (
        "Output: The DP table uses '-' for amounts that cannot be formed"
    ),
    "test_final_result_contains_minimum_equation_and_breakdown": (
        "Output: The minimum, coin equation, and breakdown are displayed"
    ),
    "test_unreachable_run_displays_clear_message": (
        "Integration: A complete impossible case displays a clear final message"
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
            "TestCoinChangeAlgorithm": "ALGORITHM AND EDGE-CASE TESTS",
            "TestInputValidation": "INPUT AND DATA-VALIDATION TESTS",
            "TestSupportingFunctions": "SUPPORTING-FUNCTION TEST",
            "TestDisplayedOutput": "DISPLAYED-OUTPUT TESTS",
            "TestCompleteProgramCase": "COMPLETE PROGRAM-FLOW TEST",
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


def load_dynamic_programming_program():
    """Load the program filename without running its main function."""
    if not PROGRAM_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {PROGRAM_PATH.name}. Put this tester in the same "
            "folder as the Dynamic Programming program."
        )

    specification = importlib.util.spec_from_file_location(
        "dynamic_programming",
        PROGRAM_PATH,
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


dynamic_programming = load_dynamic_programming_program()


class TestCoinChangeAlgorithm(unittest.TestCase):
    """Checks minimum-coin calculations, reconstruction, and edge cases."""

    def test_non_greedy_case_finds_optimal_solution(self):
        selected, dp, chosen = dynamic_programming.coin_change_minimum(
            [1, 3, 4], 6
        )

        self.assertEqual(selected, [3, 3])
        self.assertEqual(dp[6], 2)
        self.assertEqual(chosen[6], 3)

    def test_impossible_target_returns_none(self):
        selected, dp, chosen = dynamic_programming.coin_change_minimum(
            [4, 6], 7
        )

        self.assertIsNone(selected)
        self.assertEqual(dp[7], 8)
        self.assertEqual(chosen[7], -1)

    def test_target_smaller_than_every_coin(self):
        selected, dp, chosen = dynamic_programming.coin_change_minimum(
            [5, 10], 3
        )

        self.assertIsNone(selected)
        self.assertEqual(dp, [0, 4, 4, 4])
        self.assertEqual(chosen, [-1, -1, -1, -1])

    def test_single_denomination_reachable_target(self):
        selected, dp, _ = dynamic_programming.coin_change_minimum([5], 20)

        self.assertEqual(selected, [5, 5, 5, 5])
        self.assertEqual(dp[20], 4)

    def test_selected_coins_match_target_and_minimum_count(self):
        coins = [1, 5, 7]
        target = 18
        selected, dp, _ = dynamic_programming.coin_change_minimum(coins, target)

        self.assertIsNotNone(selected)
        self.assertEqual(sum(selected), target)
        self.assertEqual(len(selected), dp[target])
        self.assertTrue(all(coin in coins for coin in selected))

    def test_dp_values_for_known_example(self):
        _, dp, _ = dynamic_programming.coin_change_minimum([1, 3, 4], 6)

        self.assertEqual(dp, [0, 1, 2, 1, 1, 2, 2])

    def test_larger_target_uses_minimum_number_of_coins(self):
        selected, dp, _ = dynamic_programming.coin_change_minimum(
            [1, 5, 10, 25], 63
        )

        self.assertEqual(sum(selected), 63)
        self.assertEqual(len(selected), 6)
        self.assertEqual(dp[63], 6)


class TestInputValidation(unittest.TestCase):
    """Simulates user input to confirm invalid values are rejected."""

    def run_silently(self, function, *args):
        output = StringIO()
        with redirect_stdout(output):
            result = function(*args)
        return result, output.getvalue()

    @patch("builtins.input", side_effect=["abc", "0", "-3", "12"])
    def test_positive_integer_rejects_text_zero_and_negative(self, _mock_input):
        result, output = self.run_silently(
            dynamic_programming.get_positive_integer,
            "Target: ",
        )

        self.assertEqual(result, 12)
        self.assertIn("valid whole number", output)
        self.assertGreaterEqual(output.count("greater than 0"), 2)

    @patch(
        "builtins.input",
        side_effect=["", "one two", "1 0 5", "2 -1 5", "1 2 5"],
    )
    def test_denominations_reject_empty_text_and_nonpositive_values(
        self, _mock_input
    ):
        result, output = self.run_silently(
            dynamic_programming.get_coin_denominations
        )

        self.assertEqual(result, [1, 2, 5])
        self.assertIn("at least one coin denomination", output)
        self.assertIn("whole numbers separated by spaces", output)
        self.assertGreaterEqual(output.count("must be greater than 0"), 2)

    @patch("builtins.input", side_effect=["10 1 5 1 10 2"])
    def test_denominations_remove_duplicates_and_sort(self, _mock_input):
        result, output = self.run_silently(
            dynamic_programming.get_coin_denominations
        )

        self.assertEqual(result, [1, 2, 5, 10])
        self.assertEqual(output, "")


class TestSupportingFunctions(unittest.TestCase):
    """Checks the helper used to prepare the coin-breakdown table."""

    def test_coin_count_breakdown(self):
        counts = dynamic_programming.count_selected_coins([5, 1, 5, 2, 1, 5])

        self.assertEqual(counts, {5: 3, 1: 2, 2: 1})


class TestDisplayedOutput(unittest.TestCase):
    """Checks that important information is shown clearly to the user."""

    def test_input_summary_contains_coins_and_target(self):
        output = StringIO()
        with redirect_stdout(output):
            dynamic_programming.print_input_table([1, 5, 10], 16)

        displayed_text = output.getvalue()
        self.assertIn("INPUT SUMMARY", displayed_text)
        self.assertIn("1, 5, 10", displayed_text)
        self.assertIn("Target amount", displayed_text)
        self.assertIn("16", displayed_text)

    def test_dp_table_marks_unreachable_amounts(self):
        output = StringIO()
        target = 5
        infinity = target + 1

        with redirect_stdout(output):
            dynamic_programming.print_dp_table(
                [0, infinity, 1, infinity, 2, infinity], target
            )

        displayed_text = output.getvalue()
        self.assertIn("DYNAMIC PROGRAMMING TABLE", displayed_text)
        self.assertIn("cannot be formed", displayed_text)
        self.assertIn("| 1        | -", displayed_text)
        self.assertIn("| 4        | 2", displayed_text)

    def test_final_result_contains_minimum_equation_and_breakdown(self):
        output = StringIO()

        with redirect_stdout(output):
            dynamic_programming.print_result([3, 3], 6)

        displayed_text = output.getvalue()
        self.assertIn("FINAL RESULT", displayed_text)
        self.assertIn("Minimum number of coins required: 2", displayed_text)
        self.assertIn("3 + 3 = 6", displayed_text)
        self.assertIn("COIN BREAKDOWN", displayed_text)
        self.assertIn("TOTAL", displayed_text)


class TestCompleteProgramCase(unittest.TestCase):
    """Runs one full calculation with simulated keyboard input."""

    @patch("builtins.input", side_effect=["4 6", "7"])
    def test_unreachable_run_displays_clear_message(self, _mock_input):
        output = StringIO()

        with redirect_stdout(output):
            dynamic_programming.run_coin_change()

        displayed_text = output.getvalue()
        self.assertIn("MINIMUM COIN CHANGE", displayed_text)
        self.assertIn("INPUT SUMMARY", displayed_text)
        self.assertIn("DYNAMIC PROGRAMMING TABLE", displayed_text)
        self.assertIn("The target amount 7 cannot be formed", displayed_text)
        self.assertIn("[4, 6]", displayed_text)


if __name__ == "__main__":
    print("=" * 72)
    print("DYNAMIC PROGRAMMING COIN CHANGE - AUTOMATED TEST REPORT")
    print("=" * 72)
    print(f"Program checked : {PROGRAM_PATH.name}")
    print("Tests performed : algorithm, edge cases, validation, and output")
    print("-" * 72)

    test_suite = unittest.TestSuite(
        [
            unittest.defaultTestLoader.loadTestsFromTestCase(
                TestCoinChangeAlgorithm
            ),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestInputValidation),
            unittest.defaultTestLoader.loadTestsFromTestCase(
                TestSupportingFunctions
            ),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestDisplayedOutput),
            unittest.defaultTestLoader.loadTestsFromTestCase(
                TestCompleteProgramCase
            ),
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