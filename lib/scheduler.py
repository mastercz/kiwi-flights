from lib.flight import Flight
from lib.route import Route


class Scheduler:
    """
    Scheduler is responsible for building list of Routes that are valid for
    given input from the user
    """
    flightplan = None
    routes = None
    bags = 0

    def __init__(self, flightplan):
        self.routes = []
        self.flightplan = flightplan

    @staticmethod
    def parse_csv(csvfile):
        """
        Parse given CSV file with flightplan. CSV has to comply with format:

        flight_no: Flight number.
        origin, destination: Airport codes.
        departure, arrival: Dates and times of the departures/arrivals.
        base_price, bag_price: Prices of the ticket and one piece of baggage.
        bags_allowed: Number of allowed pieces of baggage for the flight.

        Args:
            csvfile (file): Open file descriptor that can be read by csv lib

        Returns:
            (list) Flight objects
        """
        import csv
        flightplan = []
        csv_reader = csv.DictReader(csvfile, delimiter=',')
        for line_num, row in enumerate(csv_reader):
            flightplan.append(Flight(row))

        return flightplan

    def filter_flightplan(self, filters):
        """
        Remove flights that won't be eligible for any of our routes

        Args:
            filters (object):

        """
        if filters.get('bags'):
            self.flightplan = [flight for flight in self.flightplan
                               if flight.bags_allowed >= filters.get('bags')]

        if filters.get('earliest'):
            self.flightplan = [flight for flight in self.flightplan
                               if flight.departure >= filters.get('earliest')]

        if filters.get('latest'):
            self.flightplan = [flight for flight in self.flightplan
                               if flight.arrival <= filters.get('latest')]

    def find_routes(self, airports):
        """
        Look for routes that go through given airports in specified order

        Args:
            airports (list): List of airport codes to travel through

        Returns:
            (list) Route
        """
        # Initialize routes from origin to all destinations
        routes = []
        for flight in self.flightplan:
            if flight.origin == airports[0]:
                route = Route(self.flightplan, airports[0], airports[1:])
                route.fly(flight)
                routes.append(route)

        # Look through the flightplan and try to reach the destination
        while True:
            # No more available flights to check for flights that haven't
            # reached their final destination yet.
            if not any(route.get_available_flights() for route in routes if route.get_remaining_destinations()):
                break

            for route in routes:
                if route.get_remaining_destinations():
                    # Still looking for available routes
                    for flight in route.get_available_flights():
                        branched_route = route.clone()
                        branched_route.fly(flight)
                        routes.append(branched_route)

                    # We need to remove the original route from which we
                    # branched-out
                    routes.remove(route)

        self.routes = [route for route in routes if not route.get_remaining_destinations()]

    def get_route_list(self, sort=None):
        """
        Get route list in requested format

        Args:
            sort (string): How to sort the results

        Returns:
            (list) Route information in json
        """
        summary = []
        for option_num, route in enumerate(self.routes):
            bags_allowed = min(flight.bags_allowed for flight in route.flights)
            total = sum(flight.get_price_with_bags(self.bags) for flight in route.flights)

            option_summary = {
                'flights': [flight.json_data() for flight in route.flights],
                'bags_allowed': bags_allowed,
                'bags_count': self.bags,
                'destination': ','.join(route.destinations),
                'origin': route.flights[-1].destination,
                'total_price': total,
                'travel_time': route.get_travel_time()[0],
            }

            summary.append(option_summary)

        if sort == 'total_price':
            summary.sort(key=lambda x: x.get('total_price'))
        elif sort == 'travel_time':
            summary.sort(key=lambda x: self.__seconds_from_time(x.get('travel_time')))

        return summary

    @staticmethod
    def __seconds_from_time(time):
        """
        Get seconds from time in format HH:MM:SS
        Args:
            time (string):

        Returns:
            (int)
        """
        h, m, s = time.split(':')
        return int(h)*3600 + int(m)*60 + int(s)
