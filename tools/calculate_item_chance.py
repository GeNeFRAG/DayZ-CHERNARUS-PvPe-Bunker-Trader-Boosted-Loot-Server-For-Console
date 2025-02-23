import random
import argparse
import numpy as np

def calculate_expected_items(num_places, chance_per_place):
    return num_places * chance_per_place

def simulate_searches(num_searches, num_places, chance_per_place):
    found_count = 0
    for _ in range(num_searches):
        if any(random.random() < chance_per_place for _ in range(num_places)):
            found_count += 1
    return found_count / num_searches

def binomial_simulation(num_searches, num_places, chance_per_place):
    trials = num_searches
    probability = 1 - (1 - chance_per_place) ** num_places
    found_count = np.random.binomial(trials, probability)
    return found_count / num_searches

def simulate_searches_multiple_areas(num_searches, num_places, chance_per_place, num_areas):
    found_count = 0
    for _ in range(num_searches):
        if any(any(random.random() < chance_per_place for _ in range(num_places)) for _ in range(num_areas)):
            found_count += 1
    return found_count / num_searches

def simulate_searches_per_area(num_searches, num_places, chance_per_place, num_areas):
    area_probabilities = []
    for area in range(num_areas):
        found_count = 0
        for _ in range(num_searches):
            if any(random.random() < chance_per_place for _ in range(num_places)):
                found_count += 1
        area_probabilities.append(found_count / num_searches)
    return area_probabilities

def main():
    parser = argparse.ArgumentParser(description='Calculate the chance of finding an item.')
    parser.add_argument('-n', '--num_places', type=int, default=12, help='Number of places where an item can appear')
    parser.add_argument('-c', '--chance_per_place', type=float, default=0.4, help='Chance of an item being in each place')
    parser.add_argument('-s', '--num_searches', type=int, default=200, help='Number of searches to simulate')
    parser.add_argument('-a', '--num_areas', type=int, default=1, help='Number of different areas to search')

    args = parser.parse_args()

    expected_items = calculate_expected_items(args.num_places, args.chance_per_place)
    probability_of_finding_simulation = simulate_searches(args.num_searches, args.num_places, args.chance_per_place)
    probability_of_finding_binomial = binomial_simulation(args.num_searches, args.num_places, args.chance_per_place)
    probability_of_finding_multiple_areas = simulate_searches_multiple_areas(args.num_searches, args.num_places, args.chance_per_place, args.num_areas)
    probability_of_finding_per_area = simulate_searches_per_area(args.num_searches, args.num_places, args.chance_per_place, args.num_areas)

    print(f"Expected number of items: {expected_items}")
    print(f"Probability of finding the item in {args.num_searches} searches (simulation): {probability_of_finding_simulation * 100:.2f}%")
    print(f"Probability of finding the item in {args.num_searches} searches (binomial): {probability_of_finding_binomial * 100:.2f}%")
    print(f"Probability of finding the item in {args.num_searches} searches across {args.num_areas} areas: {probability_of_finding_multiple_areas * 100:.2f}%")
    for i, prob in enumerate(probability_of_finding_per_area, 1):
        print(f"Probability of finding the item in area {i}: {prob * 100:.2f}%")

if __name__ == "__main__":
    main()
