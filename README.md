# Flight Scheduler
Flight Scheduler is a script, that for a given flight data in a form of 
csv file (check the examples), prints out a structured list of all flight 
combinations for a selected route between airports A -> B [ -> C...], sorted 
by the final price for the trip.


### Search restrictions
- By default you're performing search on ALL available combinations, according to search parameters.
- In case of a combination of A -> B -> C, the layover time in B should **not be less than 1 hour and more than 6 hours**.
- No repeating airports in the same trip!
  - A -> B -> A -> C is not a valid combination for search A -> C.
- Output is sorted by the final price of the trip.
  
*When more than 2 airports are selected*
- We want to reach all airports in given order 
- We want to stay at least 12 hours in each destination 
- Trip between selected airports are considered as individual, therefore the 
destinations can appear more than once in whole A->C, but not within A->B or B->C

# Flight plan source file
Flight plan file containing list of available flights has to be stored in the
following CSV format:

- `flight_no`: Flight number.
- `origin`, `destination`: Airport codes.
- `departure`, `arrival`: Dates and times of the departures/arrivals.
- `base_price`, `bag_price`: Prices of the ticket and one piece of baggage.
- `bags_allowed`: Number of allowed pieces of baggage for the flight.

# Script usage

```
usage: Look for flights [-h] --flightplan-file FLIGHTS_FILE [--bags BAGS]
                        [--earliest-departure EARLIEST]
                        [--latest-arrival LATEST]
                        [airports [airports ...]]

positional arguments:
  airports              List of 3 letter airport codes. All providedairports
                        will be visited in given order. Example of return trip
                        with stops (12h+) in LAX and FRA: PRG LAX FRA PRG

optional arguments:
  -h, --help            show this help message and exit
  --flightplan-file FLIGHTS_FILE
                        File path to CSV file containing list of all available
                        flights.
  --bags BAGS           Number of checked-in bags
  --earliest-departure EARLIEST
                        Earliest considered departure, format YYYY-mm-dd
  --latest-arrival LATEST
                        Latest considered arrival, format YYYY-mm-dd
  --sort {total_price,travel_time}
                        How to sort results                        
```

Execution example:

```
python flights.py RFZ WIW RFZ --flightplan-file example/example0.csv
```


#### Output
The output will be a json-compatible structured list of trips sorted by price. The trip has the following schema:

| Field          | Description                                                   |
|----------------|---------------------------------------------------------------|
| `flights`      | A list of flights in the trip according to the input dataset. |
| `origin`       | Origin airport of the trip.                                   |
| `destination`  | The final destination of the trip.                            |
| `bags_allowed` | The number of allowed bags for the trip.                      |
| `bags_count`   | The searched number of bags.                                  |
| `total_price`  | The total price for the trip.                                 |
| `travel_time`  | The total travel time.                                        |

**For more information, check the example section.**


## Example 
```bash
python flights.py WIW RFZ ECV --flightplan-file example/example0.csv --bags 1 --earliest-departure 2021-09-09 --sort travel_time
```
and get the following result:

```json
[
  {
    "flights": [
      {
        "flight_no": "ZH214",
        "origin": "WIW",
        "destination": "RFZ",
        "departure": "2021-09-04T23:20:00",
        "arrival": "2021-09-05T03:50:00",
        "base_price": 168.0,
        "bag_price": 12.0,
        "bags_allowed": 2
      },
      {
        "flight_no": "ZH665",
        "origin": "RFZ",
        "destination": "ECV",
        "departure": "2021-09-05T17:40:00",
        "arrival": "2021-09-05T20:10:00",
        "base_price": 58.0,
        "bag_price": 12.0,
        "bags_allowed": 2
      }
    ]
  }
]
```
