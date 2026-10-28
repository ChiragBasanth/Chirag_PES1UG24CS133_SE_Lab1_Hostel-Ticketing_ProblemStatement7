"""Campus shuttle timetable and fleet tracker.

Logs passenger counts per trip, works out average loads per route,
flags under-used routes and syncs the fleet data to a JSON file.
"""
import json
import secrets
from datetime import datetime

# Global state
routes = {"R1": {"name": "Main Gate - Library", "trips": []},
          "R2": {"name": "Hostel - Sports Complex", "trips": []},
          "R3": {"name": "Admin Block - Metro", "trips": []}}
MIN_CAPACITY = 10
DRIVERS = ["Prakash", "Leela", "Imran", "Tom"]


def _get_route(route_id):
    """Return the record for route_id, or raise ValueError if unknown."""
    if route_id not in routes:
        raise ValueError(f"Unknown route: {route_id!r}")
    return routes[route_id]


def add_trip_log(route_id, passenger_count, logs=None):
    """Record the passenger count for one trip and return the log list.

    Raises ValueError for an unknown route or a passenger count that is
    not a whole number of 0 or more. Nothing is recorded in that case.
    """
    route = _get_route(route_id)
    if (isinstance(passenger_count, bool)
            or not isinstance(passenger_count, int)
            or passenger_count < 0):
        raise ValueError(
            f"Invalid passenger count for {route_id}: {passenger_count!r}")
    if logs is None:
        logs = []
    route["trips"].append(passenger_count)
    logs.append(f"{datetime.now()}: {route_id} carried {passenger_count}")
    return logs


def remove_route(route_id):
    """Delete a route; raises ValueError if it does not exist."""
    _get_route(route_id)
    del routes[route_id]


def average_load(route_id):
    """Return the mean passengers per trip, or None if no trips are logged."""
    trips = _get_route(route_id)["trips"]
    if not trips:
        return None
    return sum(trips) / len(trips)


def underused_routes():
    """Return ids of routes whose average load is below MIN_CAPACITY.

    Routes with no logged trips have no average and are not flagged.
    """
    flagged = []
    for route_id in routes:
        load = average_load(route_id)
        if load is not None and load < MIN_CAPACITY:
            flagged.append(route_id)
    return flagged


def assign_driver(route_id):
    """Pick a driver at random for an existing route."""
    _get_route(route_id)
    return secrets.choice(DRIVERS)


def sync_fleet_data(file="fleet.json"):
    """Write the routes to a JSON file, then reload them from it."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(routes, handle)
    with open(file, encoding="utf-8") as handle:
        saved = json.load(handle)
    routes.clear()
    routes.update(saved)


def main():
    """Run the demo: log sample trips, report, sync and look up a route."""
    sample_trips = [("R1", 32), ("R1", 28), ("R2", 4), ("R2", -6),
                    ("R3", "full")]
    for route_id, count in sample_trips:
        try:
            add_trip_log(route_id, count)
        except ValueError as err:
            print("Rejected trip:", err)
    print("Driver for R1:", assign_driver("R1"))
    print("Underused:", underused_routes())
    print("R1 average:", average_load("R1"))
    try:
        sync_fleet_data()
    except OSError as err:
        print("Could not sync fleet data:", err)
    remove_route("R3")
    try:
        choice = input("Route to look up (Enter for R2): ")
    except EOFError:
        choice = ""
    choice = choice.strip().upper() or "R2"
    if choice in routes:
        print("Trips on", choice, ":", routes[choice]["trips"])
    else:
        print("No such route:", choice)
    try:
        print("R3 average:", average_load("R3"))
    except ValueError as err:
        print("R3 average:", err)


if __name__ == "__main__":
    main()
