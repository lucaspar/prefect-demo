"""Example of an ETL job to be run with Prefect."""

import random
from pathlib import Path

import loguru
import polars as pl
import prefect
from rich import traceback

# better stacktrace printing
traceback.install()
log = loguru.logger
FLOW_NAME = "cup-of-mud"


@prefect.task
def extract(path: Path) -> pl.DataFrame:
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
        "Grading Date": pl.Utf8,
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
        "Expiration": pl.Utf8,
        "Certification Body": pl.Categorical,
        "Certification Address": pl.Categorical,
        "Certification Contact": pl.Categorical,
    }
    return pl.read_csv(path, schema_overrides=dataframe_schema)


@prefect.task  # pyright: ignore[reportUnknownMemberType]
def transform(df_coffee: pl.DataFrame):
    """Correlates the total production weight with the moisture percentage."""
    # use kg as the normalized unit and convert the column to float
    df_coffee = df_coffee.with_columns(
        pl.col("Bag Weight")
        .str.replace(" kg", "")
        .cast(pl.Float64)
        .alias("Bag Weight Normalized"),
    )
    df_coffee = df_coffee.with_columns(
        (pl.col("Number of Bags") * pl.col("Bag Weight Normalized")).alias(
            "Total Production Weight",
        ),
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
    return df_coffee.select(selected_columns).sort(
        "Country of Origin",
        descending=True,
    )


@prefect.task  # pyright: ignore[reportUnknownMemberType]
def load(df_coffee: pl.DataFrame, path: Path) -> None:
    """Loads the data into a parquet file."""
    df_coffee.write_parquet(path)


def flow_failure_handler(flow: prefect.Flow, flow_run, state: prefect.State) -> None:
    """Define a failure handler for the flow."""
    log.info("All retries have failed! Here's the state:")
    log.info(
        f" ❌ Run of Flow '{flow.name}' failed w/ state {state.name}: {state.message}"
        + f" with run time of {flow_run.estimated_run_time}.",
    )


def flow_completion_handler(flow: prefect.Flow, flow_run, state: prefect.State):
    """Define a completion handler for the flow."""
    log.info(
        f" ✅ Run of Flow '{flow.name}' completed "
        f"w/ state {state.name}: {state.message}"
        + f" with run time of {flow_run.estimated_run_time}.",
    )


def flow_cancel_handler(flow: prefect.Flow, flow_run, state: prefect.State):
    """Define a cancel handler for the flow."""
    log.info(
        f" ⚠️ Run of Flow '{flow.name}' completed w/ state {state.name}: {state.message}"
        + f" with run time of {flow_run.estimated_run_time}.",
    )
    # clean up assets here


def flow_crash_handler(flow: prefect.Flow, flow_run, state: prefect.State):
    """Define a crash handler for the flow."""
    log.info(
        f" ☠️ Run of Flow '{flow.name}' completed w/ state {state.name}: {state.message}"
        + f" with run time of {flow_run.estimated_run_time}.",
    )


@prefect.flow(  # pyright: ignore[reportUnknownMemberType]
    name=FLOW_NAME,
    on_failure=[flow_failure_handler],
    on_completion=[flow_completion_handler],
    on_cancellation=[flow_cancel_handler],
    on_crashed=[flow_crash_handler],
    retries=3,
    retry_delay_seconds=2,
    log_prints=True,
)
def etl_flow(input_file: Path, output_file: Path) -> None:
    """Defines an ETL flow to demo Prefect."""
    df_coffee = extract(input_file)
    df_coffee = transform(df_coffee)
    # simulate a stochastic failure
    coin_flip = 0.5
    if random.random() < coin_flip:
        raise ValueError(
            "❌ Task failed successfully! 👍 |"
            + "This tests the retries and failure handler.",
        )
    load(df_coffee, path=output_file)


def main() -> None:
    """Define a Prefect flow."""
    dir_data = Path("./data").resolve()
    csv_input = "df_arabica_clean.csv"
    input_file = Path(dir_data) / csv_input
    output_file = Path(dir_data) / (csv_input + ".parquet")
    etl_flow(input_file=input_file, output_file=output_file)


if __name__ == "__main__":
    main()
