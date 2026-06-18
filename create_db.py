import pandas as pd
import sqlite3

# CSV read karo
df = pd.read_csv("data/student_data.csv")

# Database connect
conn = sqlite3.connect("database/student.db")

# Table create karo
df.to_sql("students", conn, if_exists="replace", index=False)

conn.close()

print("Database created successfully!")