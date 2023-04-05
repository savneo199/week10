from pathlib import Path
import sqlite3
import pandas as pd

# ---------------------------------------------
# Define and create the database using sqlite3
# ---------------------------------------------

# Define the database file name and location
db_file = Path(__file__).parent.joinpath("paralympics.db")

# Connect to the database
connection = sqlite3.connect(db_file)

# Create a cursor object to execute SQL queries
cursor = connection.cursor()

# 'region' table definition in SQL
create_region_table = """CREATE TABLE if not exists region(
                NOC TEXT PRIMARY KEY,
                region TEXT NOT NULL,
                notes TEXT);
                """

# 'event' table definition in SQL
create_event_table = """CREATE TABLE if not exists event(
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    year INTEGER,
    location TEXT,
    lat FLOAT,
    lon FLOAT,
    NOC TEXT,
    start TEXT,
    end TEXT,
    disabilities_included TEXT,
    events INTEGER,
    sports INTEGER,
    countries INTEGER,
    male INTEGER,
    female INTEGER,
    participants INTEGER,
    highlights TEXT,
    FOREIGN KEY(NOC) REFERENCES region(NOC));"""

# Create the tables in the database
cursor.execute(create_region_table)
cursor.execute(create_event_table)

# Commit the changes
connection.commit()

# -------------------------
# Add the data using pandas
# -------------------------

# Read the noc_regions data to a pandas dataframe
na_values = [
    "",
    "#N/A",
    "#N/A N/A",
    "#NA",
    "-1.#IND",
    "-1.#QNAN",
    "-NaN",
    "-nan",
    "1.#IND",
    "1.#QNAN",
    "<NA>",
    "N/A",
    "NULL",
    "NaN",
    "n/a",
    "nan",
    "null",
]
noc_file = Path(__file__).parent.joinpath("regions.csv")
noc_regions = pd.read_csv(noc_file, keep_default_na=False, na_values=na_values)

# Read the paralympics event data to a pandas dataframe
event_file = Path(__file__).parent.joinpath("events.csv")
paralympics = pd.read_csv(event_file)

# Write the data to tables in a sqlite database
noc_regions.to_sql(
    "region",
    connection,
    if_exists="append",
    index=False,
)
paralympics.to_sql("event", connection, if_exists="append", index=False)

# close the database connection
connection.close()
