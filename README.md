# Demo of Prefect Flow

Using [`uv`](https://docs.astral.sh/uv/guides/integration/docker/#installing-uv) to manage packages.

1. Download the data from [Kaggle](https://www.kaggle.com/datasets/fatihb/coffee-quality-data-cqi?resource=download) and extract the CSV to `data/`.
2. `uv run main.py`
3. Optionally visualize the generated table:

   `parquet-tools show data/df_arabica_clean.csv.parquet`
