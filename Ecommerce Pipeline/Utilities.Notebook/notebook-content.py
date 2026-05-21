# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

from pyspark.sql.types import StructType

def read_parquet_df(
    path: str,
    schema: StructType | None = None
):
    """
    Reusable function to read parquet files in PySpark.

    Parameters:
    - path   : File path / folder / wildcard
    - schema : StructType to enforce schema

    Returns:
    - DataFrame
    """

    reader = spark.read
    
    if schema:
        reader = reader.schema(schema)

    df = reader.parquet(path)
    return df

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
