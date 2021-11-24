from datetime import timedelta


class Route:
    """
    Route is a set of flights that can be taken in order to reach destinations
    in given order.
    """
    flights = None
    flightplan = None
    origin = None
    destination = None
    flight_log = None

    def __init__(self, flightplan, origin, destinations):
        """
        Init new Route object

        Args:
            flightplan (list): list of Flight to consider
            origin (str): Aiport code for starting point
            destinations (list): Ordered ist of airport codes to travel through
        """
        self.flights = []
        self.flight_log = []
        self.flightplan = flightplan
        self.origin = origin
        self.destinations = destinations
        import random
        self.id = random.randint(100000, 999999)

    def clone(self):
        """
        Make a valid copy of this object
        Returns:
            Route
        """
        route = Route(self.flightplan.copy(), self.origin, self.destinations)
        route.flights = list(self.flights)
        route.flight_log = list(self.flight_log)
        return route

    def get_travel_time(self):
        """
        Calculate total travel time and return result in hours:minutes:seconds

        Returns:
            (string) travel time
        """
        diff = abs(self.flights[0].departure - self.flights[-1].arrival)
        hours = str(diff.days * 24 + diff.seconds // 3600)
        minutes = str((diff.seconds % 3600) // 60).zfill(2)
        seconds = str(diff.seconds % 60).zfill(2)
        total_seconds = diff.days * 24 * 60 + diff.seconds
        return ':'.join((hours, minutes, seconds)), total_seconds

    def get_available_flights(self):
        """
        Try to fly to the next airport, unless we already reached our destination

        Returns:
            (list) All Flights that can be taken considering all constrains
        """
        available_flights = []
        for flight in self.flightplan:
            # Our current origin doesn't match flight origin, skip this immediately.
            # Can't be removed from flightplan as this might match ifuture comparisons
            if flight.origin != self.flights[-1].destination:
                continue

            # Don't want to make a loop and go through airports we already visited,
            # unless
            if flight.destination in self.skip_airports():
                continue

            if self.is_in_destination():
                # We want to stay at least 12 hours in destination
                if flight.departure < self.flights[-1].arrival + timedelta(hours=12):
                    continue
            else:
                # Connecting flight is too early (won't manage to catch it)
                if flight.departure < self.flights[-1].arrival + timedelta(hours=1):
                    continue

                # Connecting flight is too late
                if flight.departure > self.flights[-1].arrival + timedelta(hours=6):
                    continue

            available_flights.append(flight)

        return available_flights

    def fly(self, flight):
        """
        Attempt to use given flight on this route.

        Args:
            flight (Flight):

        Returns:
            None
        """
        if self.flights:
            # Apply some basic consistency checks
            if self.flights[-1].destination != flight.origin:
                raise ValueError("Last flight arrived to {} - cannot leave from {}"
                                 "".format(self.flights[-1].destination, flight.origin))

            if self.flights[-1].arrival > flight.departure:
                raise ValueError("Last flight arrived at {} - cannot depart at {}"
                                 "".format(self.flights[-1].arrival, flight.departure))

        self.flights.append(flight)

        path = []
        for flight in self.flights:
            path.append("     Leaving with flight {}  at {} from {} to {}, arrival {}"
                        "".format(flight.flight_no, flight.departure, flight.origin,
                                  flight.destination, flight.arrival))

        self.flight_log.append(
            "   Taking flight: {} -> {} ({})\n"
            "   Taken flights: {}\n"
            "   My Path: \n{} \n"
            "   Current time: {}\n"
            "   Skip airports: {}\n"
            "   Available flights: {}\n"
            "   Missing destinations: {}\n"
            "".format(flight.origin, flight.destination, flight.departure,
                      len(self.flights),
                      '\n'.join(path),
                      self.flights[0].departure,
                      ','.join(self.skip_airports()),
                      len(self.get_available_flights()),
                      ','.join(self.get_remaining_destinations())),
        )

    def get_remaining_destinations(self):
        """
        Get list of destinations we haven't reached yet

        Returns:
            (list) airport codes
        """
        remaining = self.destinations.copy()
        for flight in self.flights:
            if flight.destination == remaining[0]:
                remaining.pop(0)

        return remaining

    def is_in_destination(self):
        """
        Check if our last flight has reached intended our next planned destination

        Returns:
            (bool)
        """
        remaining = self.destinations.copy()
        in_dest = False
        # Check if last flight has reached next destination
        for flight in self.flights:
            if flight.destination == remaining[0]:
                remaining.pop(0)
                in_dest = True
            else:
                # Latest flight goes somewhere else
                in_dest = False

        return in_dest

    def skip_airports(self):
        """
        Get list of all airports that can't be visited to avoid cyclical paths

        Returns:
            (list) airport code
        """
        destinations = self.destinations.copy()
        visited = set()

        for flight in self.flights:
            visited.add(flight.origin)
            visited.add(flight.destination)
            if flight.destination == destinations[0]:
                # We will reset forbidden airports when we reach our
                # next destination
                visited = set()
                destinations.pop()

        return visited
