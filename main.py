"""Example of an ETL job to be run with Prefect."""
import os

import polars as pl
import prefect
from rich import traceback

# better stacktrace printing
traceback.install()


@prefect.task
def extract(path: str) -> pl.DataFrame:
    """Extracts the data from the given path."""
    # set the correct types
    dataframe_schema = {
        "ID": pl.Int64,
        "Country of Origin": pl.Categorical,
        "Farm Name": pl.Categorical,
        "Lot Number": pl.Categorical,
        "Mill": pl.Categorical,
        "ICO Number": pl.Categorical,
        "Company": pl.Categorical,
        "Altitude": pl.Categorical,
        "Region": pl.Categorical,
        "Producer": pl.Categorical,
        "Number of Bags": pl.Int64,
        # string type because of weight unit
        "Bag Weight": pl.Utf8,
        "In-Country Partner": pl.Categorical,
        # string type because of double year: e.g. 2013 / 2014
        "Harvest Year": pl.Utf8,
        "Grading Date": pl.Date,
        "Owner": pl.Categorical,
        "Variety": pl.Categorical,
        "Status": pl.Categorical,
        "Processing Method": pl.Categorical,
        "Aroma": pl.Float64,
        "Flavor": pl.Float64,
        "Aftertaste": pl.Float64,
        "Acidity": pl.Float64,
        "Body": pl.Float64,
        "Balance": pl.Float64,
        "Uniformity": pl.Float64,
        "Clean Cup": pl.Float64,
        "Sweetness": pl.Float64,
        "Overall": pl.Float64,
        "Defects": pl.Float64,
        "Total Cup Points": pl.Float64,
        "Moisture Percentage": pl.Float64,
        "Category One Defects": pl.Int64,
        "Quakers": pl.Int64,
        "Color": pl.Categorical,
        "Category Two Defects": pl.Int64,
        "Expiration": pl.Date,
        "Certification Body": pl.Categorical,
        "Certification Address": pl.Categorical,
        "Certification Contact": pl.Categorical,
    }
    df_coffee = pl.read_csv(path, dtypes=dataframe_schema)
    return df_coffee


@prefect.task
def transform(df_coffee: pl.DataFrame):
    """Correlates the total production weight with the moisture percentage."""
    # use kg as the normalized unit and convert the column to float
    df_coffee = df_coffee.with_columns(
        pl.col("Bag Weight")
        .str.replace(" kg", "")
        .cast(pl.Float64)
        .alias("Bag Weight Normalized")
    )
    df_coffee = df_coffee.with_columns(
        (pl.col("Number of Bags") * pl.col("Bag Weight Normalized")).alias(
            "Total Production Weight"
        )
    )
    selected_columns = [
        "ID",
        "Company",
        "Country of Origin",
        "Total Production Weight",
        "Altitude",
        "Aroma",
        "Body",
    ]
    df_coffee = df_coffee.select(selected_columns).sort(
        "Country of Origin", descending=True
    )
    return df_coffee


@prefect.task
def load(df_coffee: pl.DataFrame, path: str) -> None:
    """Loads the data into a parquet file."""
    df_coffee.write_parquet(path)


@prefect.flow
def etl_flow(input_file: str, output_file: str):
    """Defines an ETL flow to demo Prefect."""
    df_coffee = extract(input_file)
    df_coffee = transform(df_coffee)
    load(df_coffee, path=output_file)


def main():
    """Define a Prefect flow."""
    flow_name = "cup-of-mud"
    dir_data = os.path.abspath("./data")
    csv_input = "df_arabica_clean.csv"
    input_file = os.path.join(dir_data, csv_input)
    output_file = os.path.join(dir_data, csv_input + ".parquet")
    etl_flow(input_file=input_file, output_file=output_file)


if __name__ == "__main__":
    main()
