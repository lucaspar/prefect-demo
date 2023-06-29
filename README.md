# Demo of Prefect Flow

0. Install [python poetry](https://python-poetry.org/docs/#installation).
1. Download the data from [Kaggle](https://www.kaggle.com/datasets/fatihb/coffee-quality-data-cqi?resource=download) and extract the CSV to `data/`.
2. `poetry install`.
3. `poetry run python main.py`.
4. Optionally visualize the generated table:

   `parquet-tools show data/df_arabica_clean.csv.parquet`
