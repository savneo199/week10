from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

# Define the database file name and location
db_file = Path(__file__).parent.joinpath("iris.db")

# Create a connection to file as a SQLite database (this automatically creates the file if it doesn't exist)
engine = create_engine("sqlite:///" + str(db_file), echo=False)

# Read the iris data to a pandas dataframe
iris_file = Path(__file__).parent.joinpath("iris.csv")
iris = pd.read_csv(iris_file)

# Write the data to a table in the sqlite database (data/iris.db)
iris.to_sql("iris", engine, if_exists="append", index=False)
