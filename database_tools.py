import sqlite3
import sys
import pandas as pd

def initialize_database(name='Quotes'):
    # Initialize database with single table containing basic info about securities used for scraping
    path = 'C:/VSCode/project-saturday/'
    if name[-3:] != '.db':
        name = name + '.db'
    db_conn = sqlite3.connect(path+name)
    db_cursor = db_conn.cursor()
    db_cursor.execute('PRAGMA FOREIGN_KEYS = ON')
    sql = """CREATE TABLE IF NOT EXISTS TickerInfo(
    NAME VARCHAR(40) NOT NULL,
    ISIN VARCHAR(20) PRIMARY KEY,
    COUNTRY VARCHAR(20) NOT NULL,
    AVANZA_ID INTEGER
    )"""
    db_cursor.execute(sql)
    db_conn.commit()
    db_conn.close()
    print('Database initialized sucessfully!')

def insert_security(db_cursor, record):
    # Insert security to inital table with scraping information such as the securities Avanza-specific ID.
    record = [r.strip() if isinstance(r, str) else r for r in record]
    checksum = 0
    if len(record) != 4:
        print('Invalid insertion: Wrong number of elements')
        sys.exit(1)
    if isinstance(record[0], str):
        checksum += 1
    if isinstance(record[1], str):
        checksum += 1
    if isinstance(record[3], str) and len(record[3])==2:
        checksum += 1
    if isinstance(record[1], int):
        checksum += 1
    
    if checksum == 4:
        sql = f"""INSERT OR REPLACE INTO TickerInfo 
                  (ID, NAME, ISIN, COUNTRY) 
                  VALUES({record[0]}, "{record[1]}", "{record[2]}", "{record[3]}");"""
        db_cursor.execute(sql)
    else:
        print('Invalid insertion: Wrong datatype(s)')
        sys.exit(1)

def initialize_quote_table(db_cursor):
    pass

initialize_database()