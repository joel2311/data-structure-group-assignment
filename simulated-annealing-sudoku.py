import math
import random


# A sample puzzle. Zero means that the cell is empty.
SAMPLE_PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


# Displays a Sudoku grid in an easy-to-read format.
def print_grid(grid):
    print("+-------+-------+-------+")
    for row in range(9):
        print("|", end=" ")
        for column in range(9):
            print(grid[row][column], end=" ")
            if (column + 1) % 3 == 0:
                print("|", end=" ")
        print()
        if (row + 1) % 3 == 0:
            print("+-------+-------+-------+")


# Checks that the starting clues do not repeat in any row, column, or box.
def is_valid_puzzle(puzzle):
    # Check every row.
    for row in puzzle:
        clues = [number for number in row if number != 0]
        if len(clues) != len(set(clues)):
            return False

    # Check every column.
    for column in range(9):
        clues = [
            puzzle[row][column]
            for row in range(9)
            if puzzle[row][column] != 0
        ]
        if len(clues) != len(set(clues)):
            return False

    # Check every 3x3 box.
    for box_row in range(0, 9, 3):
        for box_column in range(0, 9, 3):
            clues = []
            for row in range(box_row, box_row + 3):
                for column in range(box_column, box_column + 3):
                    if puzzle[row][column] != 0:
                        clues.append(puzzle[row][column])
            if len(clues) != len(set(clues)):
                return False

    return True


# Reads a custom Sudoku puzzle from the user.
def read_puzzle():
    puzzle = []
    print("\nEnter 9 rows. Use 0 or . for an empty cell.")
    print("Example row: 530070000\n")

    for row_number in range(1, 10):
        while True:
            text = input(f"Row {row_number}: ").replace(" ", "").replace(".", "0")

            if len(text) == 9 and text.isdigit():
                puzzle.append([int(character) for character in text])
                break

            print("Invalid row. Please enter exactly 9 digits.")

    return puzzle


# Records which empty cells can be changed inside each 3x3 box.
def find_changeable_cells(puzzle):
    changeable_boxes = []

    for box_row in range(0, 9, 3):
        for box_column in range(0, 9, 3):
            cells = []
            for row in range(box_row, box_row + 3):
                for column in range(box_column, box_column + 3):
                    if puzzle[row][column] == 0:
                        cells.append((row, column))
            changeable_boxes.append(cells)

    return changeable_boxes


# Fills every 3x3 box with its missing numbers in a random order.
def create_initial_solution(puzzle):
    grid = [row[:] for row in puzzle]

    for box_row in range(0, 9, 3):
        for box_column in range(0, 9, 3):
            used_numbers = set()
            empty_cells = []

            for row in range(box_row, box_row + 3):
                for column in range(box_column, box_column + 3):
                    if grid[row][column] == 0:
                        empty_cells.append((row, column))
                    else:
                        used_numbers.add(grid[row][column])

            missing_numbers = [
                number for number in range(1, 10) if number not in used_numbers
            ]
            random.shuffle(missing_numbers)

            for index in range(len(empty_cells)):
                row, column = empty_cells[index]
                grid[row][column] = missing_numbers[index]

    return grid


# Calculates the number of duplicate conflicts in all rows and columns.
# A solved Sudoku has a cost of 0.
def calculate_cost(grid):
    cost = 0

    for row in range(9):
        cost += 9 - len(set(grid[row]))

    for column in range(9):
        column_values = [grid[row][column] for row in range(9)]
        cost += 9 - len(set(column_values))

    return cost


# Solves the puzzle by repeatedly swapping two changeable cells in one box.
def simulated_annealing(
    puzzle,
    initial_temperature=2.0,
    cooling_rate=0.9997,
    iterations_per_restart=100000,
    maximum_restarts=15,
):
    changeable_boxes = find_changeable_cells(puzzle)

    # Only boxes with at least two empty cells can produce a swap.
    swappable_boxes = [box for box in changeable_boxes if len(box) >= 2]
    if not swappable_boxes:
        return [row[:] for row in puzzle], calculate_cost(puzzle), 0, 0

    best_grid = None
    best_cost = float("inf")
    total_iterations = 0

    for restart in range(1, maximum_restarts + 1):
        current_grid = create_initial_solution(puzzle)
        current_cost = calculate_cost(current_grid)
        temperature = initial_temperature

        if current_cost < best_cost:
            best_grid = [row[:] for row in current_grid]
            best_cost = current_cost

        for _ in range(iterations_per_restart):
            total_iterations += 1

            # Randomly choose two non-fixed cells from the same 3x3 box.
            box = random.choice(swappable_boxes)
            first_cell, second_cell = random.sample(box, 2)
            row1, column1 = first_cell
            row2, column2 = second_cell

            # Make the temporary swap and measure the new cost.
            current_grid[row1][column1], current_grid[row2][column2] = (
                current_grid[row2][column2],
                current_grid[row1][column1],
            )
            new_cost = calculate_cost(current_grid)
            cost_change = new_cost - current_cost

            # Always accept an improvement. Sometimes accept a worse move
            # so that the search can escape a local minimum.
            accept_move = cost_change <= 0
            if not accept_move and temperature > 0:
                probability = math.exp(-cost_change / temperature)
                accept_move = random.random() < probability

            if accept_move:
                current_cost = new_cost
            else:
                # Undo the swap when the move is rejected.
                current_grid[row1][column1], current_grid[row2][column2] = (
                    current_grid[row2][column2],
                    current_grid[row1][column1],
                )

            if current_cost < best_cost:
                best_grid = [row[:] for row in current_grid]
                best_cost = current_cost

            if best_cost == 0:
                return best_grid, best_cost, total_iterations, restart

            temperature *= cooling_rate

    return best_grid, best_cost, total_iterations, maximum_restarts


# Controls the console menu, input, solving process, and final output.
def main():
    print("SUDOKU SOLVER USING SIMULATED ANNEALING")
    print("1. Use the sample puzzle")
    print("2. Enter my own puzzle")

    while True:
        choice = input("Choose 1 or 2: ").strip()
        if choice == "1":
            puzzle = [row[:] for row in SAMPLE_PUZZLE]
            break
        if choice == "2":
            puzzle = read_puzzle()
            break
        print("Invalid choice. Please enter 1 or 2.")

    if not is_valid_puzzle(puzzle):
        print("\nThe puzzle is invalid because some starting clues conflict.")
        return

    print("\nStarting puzzle:")
    print_grid(puzzle)
    print("\nSearching for a solution...")

    solution, cost, iterations, restarts = simulated_annealing(puzzle)

    print("\nBest result:")
    print_grid(solution)
    print(f"Final cost: {cost}")
    print(f"Iterations used: {iterations}")
    print(f"Restarts used: {restarts}")

    if cost == 0:
        print("Status: A valid Sudoku solution was found.")
    else:
        print("Status: No complete solution was found in this run.")
        print("This can happen because simulated annealing is a heuristic.")


if __name__ == "__main__":
    main()