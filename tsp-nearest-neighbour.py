"""
Travelling Salesman Problem using the Nearest Neighbour Heuristic.

The program asks the user to enter cities and the distances between them.
It then visits the nearest unvisited city until every city has been visited,
before returning to the starting city.

Important:
The Nearest Neighbour Heuristic finds a good route quickly, but it does not
always guarantee the shortest possible route.
"""


# Gets a valid integer from the user.
def get_integer(message, minimum):
    while True:
        try:
            value = int(input(message))

            if value < minimum:
                print(f"Please enter a number greater than or equal to {minimum}.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a whole number.")


# Gets the city names and makes sure that every name is unique.
def get_city_names(number_of_cities):
    cities = []

    print("\nEnter the name of each city.")

    for city_number in range(1, number_of_cities + 1):
        while True:
            city_name = input(f"City {city_number}: ").strip()

            if city_name == "":
                print("City name cannot be empty.")
            elif city_name.lower() in [city.lower() for city in cities]:
                print("That city name has already been entered.")
            else:
                cities.append(city_name)
                break

    return cities


# Gets a valid non-negative distance from the user.
def get_distance(message):
    while True:
        try:
            distance = float(input(message))

            if distance < 0:
                print("Distance cannot be negative.")
            else:
                return distance
        except ValueError:
            print("Invalid input. Please enter a number.")


# Creates a symmetric distance matrix using distances entered by the user.
def get_distance_matrix(cities):
    number_of_cities = len(cities)
    distances = []

    # First, create a matrix filled with zeros.
    for row in range(number_of_cities):
        distances.append([0.0] * number_of_cities)

    print("\nEnter the distance between each pair of cities.")

    # Only one direction is requested because A to B equals B to A.
    for first_city in range(number_of_cities):
        for second_city in range(first_city + 1, number_of_cities):
            message = (
                f"Distance from {cities[first_city]} "
                f"to {cities[second_city]}: "
            )
            distance = get_distance(message)

            distances[first_city][second_city] = distance
            distances[second_city][first_city] = distance

    return distances


# Displays the distances in a simple table.
def display_distance_matrix(cities, distances):
    width = max(10, max(len(city) for city in cities) + 2)

    print("\nDISTANCE MATRIX")
    print("-" * (width * (len(cities) + 1)))
    print("".ljust(width), end="")

    for city in cities:
        print(city.ljust(width), end="")

    print()

    for row in range(len(cities)):
        print(cities[row].ljust(width), end="")

        for column in range(len(cities)):
            value = f"{distances[row][column]:g}"
            print(value.ljust(width), end="")

        print()

    print("-" * (width * (len(cities) + 1)))


# Lets the user choose a starting city by entering its displayed number.
def get_starting_city(cities):
    print("\nChoose the starting city:")

    for index in range(len(cities)):
        print(f"{index + 1}. {cities[index]}")

    choice = get_integer("Enter your choice: ", 1)

    while choice > len(cities):
        print(f"Please enter a number from 1 to {len(cities)}.")
        choice = get_integer("Enter your choice: ", 1)

    return choice - 1


# Finds a route by repeatedly selecting the nearest unvisited city.
def nearest_neighbour(cities, distances, starting_city):
    number_of_cities = len(cities)
    visited = [False] * number_of_cities
    route = [starting_city]
    journey_steps = []
    total_distance = 0.0
    current_city = starting_city

    visited[current_city] = True

    # Continue until the route contains every city.
    while len(route) < number_of_cities:
        nearest_city = -1
        nearest_distance = float("inf")

        # Manually search for the nearest city that has not been visited.
        for city in range(number_of_cities):
            if not visited[city] and distances[current_city][city] < nearest_distance:
                nearest_city = city
                nearest_distance = distances[current_city][city]

        journey_steps.append((current_city, nearest_city, nearest_distance))
        total_distance += nearest_distance
        current_city = nearest_city
        visited[current_city] = True
        route.append(current_city)

    # Return from the final city to the starting city.
    return_distance = distances[current_city][starting_city]
    journey_steps.append((current_city, starting_city, return_distance))
    total_distance += return_distance
    route.append(starting_city)

    return route, journey_steps, total_distance


# Displays the final route, every journey step, and the total distance.
def display_result(cities, route, journey_steps, total_distance):
    route_names = []

    for city_index in route:
        route_names.append(cities[city_index])

    print("\n" + "=" * 58)
    print("TRAVELLING SALESMAN PROBLEM RESULT")
    print("=" * 58)
    print("Method : Nearest Neighbour Heuristic")
    print("Route  : " + " -> ".join(route_names))

    print("\nJOURNEY SUMMARY")
    print("-" * 58)
    print(f"{'Step':<8}{'From':<15}{'To':<15}{'Distance':>12}")
    print("-" * 58)

    for step_number in range(len(journey_steps)):
        from_city, to_city, distance = journey_steps[step_number]

        print(
            f"{step_number + 1:<8}"
            f"{cities[from_city]:<15}"
            f"{cities[to_city]:<15}"
            f"{distance:>12g}"
        )

    print("-" * 58)
    print(f"{'Total distance:':<38}{total_distance:>12g}")
    print("=" * 58)
    print(
        "\nNote: This is a heuristic solution. It aims to find a good\n"
        "route efficiently, but it may not be the optimal route."
    )


# Controls the overall flow of the console program.
def main():
    print("=" * 58)
    print("TSP USING THE NEAREST NEIGHBOUR HEURISTIC")
    print("=" * 58)

    number_of_cities = get_integer(
        "Enter the number of cities (minimum 2): ",
        2,
    )

    cities = get_city_names(number_of_cities)
    distances = get_distance_matrix(cities)

    display_distance_matrix(cities, distances)

    starting_city = get_starting_city(cities)
    route, journey_steps, total_distance = nearest_neighbour(
        cities,
        distances,
        starting_city,
    )

    display_result(cities, route, journey_steps, total_distance)


# Runs the program only when this file is executed directly.
if __name__ == "__main__":
    main()