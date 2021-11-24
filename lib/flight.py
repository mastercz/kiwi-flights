from datetime import datetime


class Flight:
    """
    Flight object represents parsed data from our flightplan
    """
    flight_no = None
    origin = None
    destination = None
    departure = None
    arrival = None
    base_price = 0
    bag_price = 0
    bags_allowed = 0

    def __init__(self, data):
        self.flight_no = data['flight_no']
        self.origin = data['origin']
        self.destination = data['destination']
        self.departure = datetime.strptime(data['departure'], "%Y-%m-%dT%H:%M:%S")
        self.arrival = datetime.strptime(data['arrival'], "%Y-%m-%dT%H:%M:%S")
        self.base_price = float(data['base_price'])
        self.bag_price = float(data['bag_price'])
        self.bags_allowed = int(data['bags_allowed'])

    def json_data(self):
        """
        Gives flight data in expected json format

        Returns:
            (dict)
        """
        return {
            'flight_no': self.flight_no,
            'origin': self.origin,
            'destination': self.destination,
            'departure': self.departure.strftime("%Y-%m-%dT%H:%M:%S"),
            'arrival': self.arrival.strftime("%Y-%m-%dT%H:%M:%S"),
            'base_price': self.base_price,
            'bag_price': self.bag_price,
            'bags_allowed': self.bags_allowed
        }

    def get_price_with_bags(self, bags):
        """
        Get total price including bags

        Args:
            bags (int): Bag count

        Returns:
            (float): Total price
        """
        return self.base_price + self.bag_price * bags

    def __str__(self):
        """
        A more user-friendly representation of Flight object
        """
        return "[{}] {}->{} ({}->{})".format(self.flight_no, self.origin,
                                             self.destination, self.departure,
                                             self.arrival)
