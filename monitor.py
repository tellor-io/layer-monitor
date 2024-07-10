import requests
import csv
import time
import os
import json
from datetime import datetime

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
    dt = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    unix_time = dt.timestamp()
    return unix_time

def get_block_size(block):
    block_string = json.dumps(block)
    return len(block_string)

def get_block_data(height):
    block = get_block_by_height(height)
    block_time = get_block_time(block)
    block_size = get_block_size(block)
    return {
        "height": height,
        "block_time": block_time,
        "block_size": block_size,
        "num_txs": len(block["block"]["data"]["txs"]),
        # "num_validators": len(block["block"]["header"]["validators"])
    }

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
            writer.writerow(["height", "block_time", "block_size", "num_txs"])

    latest_height = get_latest_block_height()
    
    while True:
        while latest_height > last_saved_height:
            last_saved_height += 1
            block_data = get_block_data(last_saved_height)
            print(block_data)
            with open(csv_file, "a") as file:
                writer = csv.DictWriter(file, fieldnames=block_data.keys())
                writer.writerow(block_data)

        time.sleep(poll_interval)
        latest_height = get_latest_block_height()
        print(f"Latest block height: {latest_height}")


if __name__ == "__main__":
    main()