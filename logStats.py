import requests
import csv
import time
import os
import json
from datetime import datetime
from dateutil import parser
import numpy as np

rpc_endpoint = "http://tellornode.com:26657/"
csv_file = "data/chain_data.csv"
poll_interval = 5 #seconds


def get_latest_block_height():
    response = requests.get(f"{rpc_endpoint}/status")
    return int(response.json()["result"]["sync_info"]["latest_block_height"])


# function to get latest block height and then 
def calculateAverageBlockTimeForThePast3000():
    latest_block_height = get_latest_block_height()
    block_times = []

    with open(csv_file, 'r') as data_csv:
        data = csv.DictReader(data_csv)

        for row in data[(latest_block_height - 3000):]:
            time_since_prev_block = row.get('time_since_prev_block')
            if time_since_prev_block is not None:
                block_times.append(float(time_since_prev_block))
            else:
                block_times.append(0.0)

    block_time_stats = calculate_stats(block_times)

    average_block_time = block_time_stats['mean'];
    return { "average_block_time": average_block_time, "latest_block_height":latest_block_height }   
    

def calculate_stats(data):
    return {
        'mean': np.mean(data),
        'median': np.median(data),
        'range': np.max(data) - np.min(data),
        'std': np.std(data)
    }


def calculateFutureBlockHeightBasedOnTimestamp(upgradeTimestamp):
    data = calculateAverageBlockTimeForThePast3000()
    average_block_time = data["average_block_time"]
    latest_block_height = data["latest_block_height"]
    currentTime = time.time()
    timeDifference = float(upgradeTimestamp) - currentTime
    res = float(latest_block_height) + (float(timeDifference) / float(average_block_time))

    upgradeHeight = int(res)
    return upgradeHeight

def main():
    currentTimestamp = time.time()
    hours = 26
    minutes = 30
    upgradeTimestamp = currentTimestamp + float(3600 * hours + 60 * minutes)

    calculateFutureBlockHeightBasedOnTimestamp(upgradeTimestamp)


if __name__ == '__main__':
    main()