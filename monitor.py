import requests
import csv
import time
import os
import json
from datetime import datetime
from dateutil import parser

# desired data:
# block time
# block size
# number of txs
# number of validators

# configs
rpc_endpoint = "http://localhost:26657"
csv_file = "data/chain_data.csv"
poll_interval = 5 #seconds

def get_latest_block_height():
    response = requests.get(f"{rpc_endpoint}/status")
    return int(response.json()["result"]["sync_info"]["latest_block_height"])

def get_block_by_height(height):
    response = requests.get(f"{rpc_endpoint}/block?height={height}")
    return response.json()["result"]

def get_block_time(block):
    time_string = block["block"]["header"]["time"]
    print(time_string)
    dt = parser.parse(time_string)
    microseconds = dt.timestamp()
    return microseconds

def get_block_size(block):
    block_string = json.dumps(block)
    return len(block_string)

def get_block_data(height):
    block = get_block_by_height(height)
    block_time = get_block_time(block)
    block_size = get_block_size(block)
    validator_set_size = get_validator_set_size(height)
    return {
        "height": height,
        "block_time": block_time,
        "block_size": block_size,
        "num_txs": len(block["block"]["data"]["txs"]),
        "num_validators": validator_set_size
    }

def get_validator_set_size(height):
    # http://localhost:26657/validators?height=500&page=1&per_page=100
    response = requests.get(f"{rpc_endpoint}/validators?height={height}&page=1&per_page=100")
    return len(response.json()["result"]["validators"])

def main():
    # check for existing data
    if os.path.exists(csv_file):
        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            next(reader)
            last_row = None
            for row in reader:
                last_row = row
            if last_row:
                last_saved_height = int(last_row[0])
            else:
                last_saved_height = 0
    else:
        last_saved_height = 0
        with open(csv_file, "w") as file:
            writer = csv.writer(file)
            writer.writerow(["height", "block_time", "block_size", "num_txs", "num_validators", "time_since_prev_block"])

    latest_height = get_latest_block_height()
    
    while True:
        while latest_height > last_saved_height:
            last_saved_height += 1
            block_data = get_block_data(last_saved_height)
            # if greater than 1 height, get time diff from previous block
            if last_saved_height > 1:
                block_data["time_since_prev_block"] = block_data["block_time"] - get_block_time(get_block_by_height(last_saved_height - 1))
            print(block_data)
            with open(csv_file, "a") as file:
                writer = csv.DictWriter(file, fieldnames=block_data.keys())
                writer.writerow(block_data)

        time.sleep(poll_interval)
        latest_height = get_latest_block_height()
        print(f"Latest block height: {latest_height}")


if __name__ == "__main__":
    main()