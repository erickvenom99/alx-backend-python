#!/usr/bin/env python3
"""
READ CSV
"""
import csv
import time
def csv_reader(file_path):
    """
    Function yields a row from csv
    """
    with open(file_path, 'r') as f:
        for row in csv.reader(f):
            yield row
if __name__ == "__main__":
    csv_r = "techcrunch.csv"
    for row in csv_reader(csv_r):
        print(row)
  
