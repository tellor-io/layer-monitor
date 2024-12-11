import requests
import base64
import hashlib
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
rpc_endpoint = "http://tellorlayer.com/rpc"
csv_file = "data/chain_data.csv"
gas_data_file = "data/reports_gas_data.csv"
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
    ProcessReportsForGasPrices(block)
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

def ProcessReportsForGasPrices(block_data):
    txs = block_data.get("result", {}).get("block", {}).get("data", {}).get("txs", [])
    height = block_data.get("result", {}).get("block", {}).get("height", {})
    for tx in txs:
        # Decode Base64 transaction
        decoded_tx = base64.b64decode(tx)
        # Compute SHA-256 hash
        tx_hash = hashlib.sha256(decoded_tx).hexdigest()

        # Query the transaction by hash
        tx_url = f"http://54.234.103.186:26657/tx?hash=0x{tx_hash}"
        tx_response = requests.get(tx_url)

        if tx_response.status_code != 200:
            print(f"Failed to fetch transaction {tx_hash}: {tx_response.status_code} - {tx_response.text}")
            continue

        tx_data = tx_response.json()

        sender = "unknown"
        code = ""
        try:
            raw_log = tx_data.get("result", {}).get("tx_result", {})
            log_json = json.loads(raw_log)
            code = log_json["code"]
            gas_used = log_json["gas_used"]
            if log_json and isinstance(log_json, list):
                for event in log_json["events"]:
                    if event.get("type") == "message":
                        for attr in event.get("attributes", []):
                            if attr.get("key") == "sender":
                                sender = attr.get("value")
                                break
        except (json.JSONDecodeError, KeyError, TypeError):
            print(f"Could not extract sender for transaction {tx_hash}")
        report_gas = {
            "height": height,
            "reporter": sender,
            "gas_used": gas_used,
            "result_code": code
        }
        with open(gas_data_file, "a") as file:
            reporter_gas_writer = csv.DictWriter(file, fieldnames=report_gas.keys())
            reporter_gas_writer.writerow(report_gas)
    return 0

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
            block_data_writer = csv.writer(file)
            block_data_writer.writerow(["height", "block_time", "block_size", "num_txs", "num_validators", "time_since_prev_block"])

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
        last_saved_height = 837305
        with open(csv_file, "w") as file:
            reports_gas_writer = csv.writer(file)
            reports_gas_writer.writerow(["height", "reporter", "gas_used", "result_code"])

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
                block_data_writer = csv.DictWriter(file, fieldnames=block_data.keys())
                block_data_writer.writerow(block_data)
            ProcessReportsForGasPrices(block_data=block_data)

        time.sleep(poll_interval)
        latest_height = get_latest_block_height()
        print(f"Latest block height: {latest_height}")


if __name__ == "__main__":
    main()