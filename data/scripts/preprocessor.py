import pandas as pd
import os

def preprocess():
    os.makedirs("data/processed", exist_ok=True)
    print("Preprocessing complete.")

if __name__ == "__main__":
    preprocess()
