from datetime import datetime

REG_NO = 192411188        # <-- EDIT: your registration number
NAME = "Lakshmi Gayathri"            # <-- EDIT: your name
SEED = REG_NO % 10000
SIZES = [1000, 10000, 100000, 1000000]

def header():
    print(f"Reg No: {REG_NO} | Name: {NAME} | Seed: {SEED} | {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("-" * 80)
