"""
Coin Change using Dynamic Programming

This console program finds the minimum number of coins needed to make a target
amount. It accepts user input, validates it, runs the dynamic programming
algorithm, and displays the results using tables and lists.

No external libraries are used.
"""

def get_positive_integer(prompt):
    """Read and return a positive integer from the user."""
    while True:
        value = input(prompt).strip()

        try:
            number = int(value)
            if number <= 0:
                print("Error: Please enter an integer greater than 0.\n")
                continue
            return number
        except ValueError:
            print("Error: Please enter a valid whole number.\n")


def get_coin_denominations():
    """Read, validate, remove duplicates, and sort coin denominations."""
    while True:
        raw_input = input(
            "Enter coin denominations separated by spaces (example: 1 2 5): "
        ).strip()

        try:
            coins = [int(value) for value in raw_input.split()]

            if not coins:
                print("Error: Enter at least one coin denomination.\n")
                continue

            if any(coin <= 0 for coin in coins):
                print("Error: All coin denominations must be greater than 0.\n")
                continue

            # Remove duplicated denominations and arrange them from smallest to largest.
            return sorted(set(coins))

        except ValueError:
            print("Error: Use whole numbers separated by spaces only.\n")


def coin_change_minimum(coins, target):
    """
    Find the minimum number of coins required for every amount from 0 to target.

    dp[amount] stores the minimum number of coins needed for that amount.
    chosen_coin[amount] stores the final coin used in the best solution.
    """
    infinity = target + 1
    dp = [infinity] * (target + 1)
    chosen_coin = [-1] * (target + 1)

    # Base case: zero coins are required to make amount 0.
    dp[0] = 0

    for current_amount in range(1, target + 1):
        for coin in coins:
            if coin > current_amount:
                break

            previous_amount = current_amount - coin

            # Use this coin if it creates a better solution.
            if dp[previous_amount] != infinity and dp[previous_amount] + 1 < dp[current_amount]:
                dp[current_amount] = dp[previous_amount] + 1
                chosen_coin[current_amount] = coin

    if dp[target] == infinity:
        return None, dp, chosen_coin

    # Reconstruct the selected coins by following chosen_coin backwards.
    selected_coins = []
    remaining_amount = target

    while remaining_amount > 0:
        coin = chosen_coin[remaining_amount]

        # Safety check to prevent an invalid reconstruction loop.
        if coin == -1:
            return None, dp, chosen_coin

        selected_coins.append(coin)
        remaining_amount -= coin

    return selected_coins, dp, chosen_coin


def print_input_table(coins, target):
    """Display the entered denominations and target in table form."""
    print("\nINPUT SUMMARY")
    print("+----------------------+------------------------------+")
    print("| Item                 | Value                        |")
    print("+----------------------+------------------------------+")
    print(f"| Coin denominations   | {', '.join(map(str, coins)):<28} |")
    print(f"| Target amount        | {target:<28} |")
    print("+----------------------+------------------------------+")


def print_dp_table(dp, target):
    """Display the minimum coin count calculated for each amount."""
    print("\nDYNAMIC PROGRAMMING TABLE")
    print("The symbol '-' means the amount cannot be formed.")
    print("+----------+----------------------+")
    print("| Amount   | Minimum Coins        |")
    print("+----------+----------------------+")

    infinity = target + 1
    for amount in range(target + 1):
        result = "-" if dp[amount] == infinity else str(dp[amount])
        print(f"| {amount:<8} | {result:<20} |")

    print("+----------+----------------------+")


def count_selected_coins(selected_coins):
    """Return a dictionary containing the quantity of each selected coin."""
    coin_counts = {}

    for coin in selected_coins:
        coin_counts[coin] = coin_counts.get(coin, 0) + 1

    return coin_counts


def print_result(selected_coins, target):
    """Display the final minimum-coin solution as a list and breakdown table."""
    coin_counts = count_selected_coins(selected_coins)

    print("\nFINAL RESULT")
    print(f"Minimum number of coins required: {len(selected_coins)}")
    print("Selected coins:", " + ".join(map(str, selected_coins)), "=", target)

    print("\nCOIN BREAKDOWN")
    print("+--------------+--------------+--------------+")
    print("| Coin Value   | Quantity     | Total Value  |")
    print("+--------------+--------------+--------------+")

    for coin in sorted(coin_counts, reverse=True):
        quantity = coin_counts[coin]
        total_value = coin * quantity
        print(f"| {coin:<12} | {quantity:<12} | {total_value:<12} |")

    print("+--------------+--------------+--------------+")
    print(f"| TOTAL        | {len(selected_coins):<12} | {target:<12} |")
    print("+--------------+--------------+--------------+")


def run_coin_change():
    """Run one complete coin-change calculation."""
    print("=" * 60)
    print("       MINIMUM COIN CHANGE - DYNAMIC PROGRAMMING")
    print("=" * 60)
    print("Enter all values using the same unit, such as RM or sen.\n")

    coins = get_coin_denominations()
    target = get_positive_integer("Enter the target amount: ")

    print_input_table(coins, target)

    selected_coins, dp, _ = coin_change_minimum(coins, target)
    print_dp_table(dp, target)

    if selected_coins is None:
        print("\nFINAL RESULT")
        print(f"The target amount {target} cannot be formed using {coins}.")
    else:
        print_result(selected_coins, target)


def main():
    """Main menu that allows the user to run the program more than once."""
    while True:
        run_coin_change()

        choice = input("\nWould you like to test another case? (Y/N): ").strip().lower()
        while choice not in ("y", "n"):
            choice = input("Please enter Y or N: ").strip().lower()

        if choice == "n":
            print("\nThank you for using the Coin Change program.")
            break

        print("\n")


if __name__ == "__main__":
    main()