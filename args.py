import argparse

parser = argparse.ArgumentParser(description="Create a database of anime theme timestamps.")
parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="display verbose logging")
parser.add_argument("-sa", "--skip-aggregation", dest="skip_aggregation", action="store_true", help="skips the first loop that aggregates timestamps from other databases")
parser.add_argument("-asi", "--aggregation-start-id", dest="aggregation_start", type=int, help="set the start ID for the first, aggregation, loop")
parser.add_argument("-ssi", "--scrape-start-id", dest="scrape_start", type=int, help="set the start ID for the second, scraping, loop")

parsed_args = parser.parse_args()