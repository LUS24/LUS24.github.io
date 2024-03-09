import pandas as pd
from datetime import datetime

# Metadata URL
METADATA_URL = "https://aact.ctti-clinicaltrials.org/data_dictionary"

# Date
today = datetime.today().strftime("%Y-%m-%d")

# Download the static tables

## Since we know that exactly two tables are selected
## we can use python destructuring syntax to assign the two pandas DataFrames
## to aact_tables and aact_v_and_f
aact_tables, aact_v_and_f = pd.read_html(
    METADATA_URL, attrs={"class": "dictionaryDisplay"}
)

## Save the DataFrames to CSV
aact_tables.to_csv(f"{today}_aact_tables_metadata.csv", index=False)

aact_v_and_f.to_csv(f"{today}_aact_views_functions_metadata.csv", index=False)
