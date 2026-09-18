import csv
import io
import requests
from clickhouse_driver import Client

CATALOG_URL = "https://gwosc.org/eventapi/csv/GWTC-1-confident/"

NS_MAX_MASS = 3.0

def to_float(value):
	if value is None or value == "":
		return None
	try:
		return float(value)
	except ValueError:
		return None


def classify(mass_1, mass_2):
    if mass_1 is None or mass_2 is None:
        return "UNKNOWN"

    is_ns_1 = mass_1 < NS_MAX_MASS
    is_ns_2 = mass_2 < NS_MAX_MASS

    if is_ns_1 and is_ns_2:
        return "BNS"
    if not is_ns_1 and not is_ns_2:
        return "BBH"
    return "NSBH"

def fetch_events():
	response = requests.get(CATALOG_URL, timeout=30)
	response.raise_for_status()

	reader = io.StringIO(response.text)
	dict_events = csv.DictReader(reader)
	list_events = list(dict_events)
	events = []
	for row in list_events:
		mass_1 = to_float(row["mass_1_source"])
		mass_2 = to_float(row["mass_2_source"])
		if mass_1 is None or mass_2 is None:
			continue
		total_mass = mass_1 + mass_2
		events.append([
			row["commonName"],
			to_float(row["GPS"]),
			mass_1,
			mass_2,
			total_mass,
			to_float(row["network_matched_filter_snr"]),
			to_float(row["luminosity_distance"]),
			to_float(row["redshift"]),
			row.get("catalog.shortName") or None,
			classify(mass_1, mass_2),
		])

	return events
	

def main():
	events = fetch_events()
	print(f"Скачано событий {len(events)}")

	client = Client(
		host="localhost",
		port=9000,
		user="default",
		password="clickhouse",
		database="gw_v2"
	)

	client.execute("TRUNCATE TABLE gw_v2.events")
	client.execute("""
		INSERT INTO gw_v2.events
			(common_name, gps, mass_1_source, mass_2_source,
			 total_mass_source, network_snr, luminosity_distance,
			 redshift, catalog, merger_type)
		VALUES
		""",
		events,
	)

	print("Готово")

main()



