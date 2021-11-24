import argparse
import json
import sys
from datetime import datetime

from lib.scheduler import Scheduler


def airport_code_type(code):
    """
    Check if given string has correct airport format

    Args:
        code (str): code enter by the user

    Returns:
        code in uppercase

    Raises:
        ArgumentTypeError when format is invalid
    """
    if len(code) != 3 or not str(code).isalpha():
        raise argparse.ArgumentTypeError("You have to enter 3 letter airport code (e.g. LAX)")

    return code.upper()


def parse_args():
    parser = argparse.ArgumentParser("Look for flights")
    parser.add_argument("airports", type=airport_code_type, nargs='*',
                        help="List of 3 letter airport codes. All provided"
                             "airports will be visited in given order. "
                             "Example of  return trip with stops (12h+) in "
                             "LAX and FRA: PRG LAX FRA PRG")
    parser.add_argument('--flightplan-file', dest='flights_file', required=True,
                        help="File path to CSV file containing list of all "
                             "available flights.",
                        type=argparse.FileType('r'))
    parser.add_argument('--bags', default=0, type=int,
                        help="Number of checked-in bags")
    parser.add_argument('--earliest-departure',
                        dest='earliest',
                        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                        help="Earliest considered departure, format YYYY-mm-dd")
    parser.add_argument('--latest-arrival',
                        dest='latest',
                        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                        help="Latest considered arrival, format YYYY-mm-dd")
    parser.add_argument('--sort',
                        dest='sort', default='total_price',
                        choices=['total_price', 'travel_time'],
                        help="How to sort results")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if len(args.airports) < 2:
        raise argparse.ArgumentTypeError("You need to choose at lest 2 airport codes")

    if args.bags < 0:
        raise argparse.ArgumentTypeError("Number of bags has to be a positive integer")

    return args


def main():
    args = parse_args()

    # Get all available flights
    scheduler = Scheduler(Scheduler.parse_csv(args.flights_file))

    # Filter-out flights that are not matching basic criteria
    scheduler.filter_flightplan({'bags': args.bags,
                                 'earliest': args.earliest,
                                 'latest': args.latest
                                 })
    scheduler.bags = args.bags
    scheduler.find_routes(args.airports)

    # Print result to stdout
    print(json.dumps(scheduler.get_route_list(sort=args.sort), indent=4))


if __name__ == '__main__':
    main()
