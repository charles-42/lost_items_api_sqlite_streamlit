import pandas as pd
from sqlalchemy import create_engine

# Create an engine
engine = create_engine('sqlite:///db.sqlite')


from sqlalchemy import text
with engine.begin() as conn:
    query = text("""SELECT * FROM TemperatureHeure""")
    df = pd.read_sql_query(query, conn)

df.index = pd.to_datetime(df.date,utc=True)
df = df.drop(columns=["date"])

# Group by departement and day
df_temp = df.resample('D').agg("mean")

df_temp = df_temp.reset_index()
df_temp["date"] = pd.to_datetime(df_temp["date"]).dt.date

import sqlite3 # We need to use sqlite3 like sqlalchemy >2.0 is no longer compatible with Pandas
conn = sqlite3.connect('sqlite:///../db.sqlite')


df_temp.to_sql("Temperature", conn, if_exists='append',index=False)