# generates data for subset sum problem 
# generate.py takes command line arguments,
# 1. number of files to generate with different target values
# 2. n: number of elements in the list
# 3. type of the data to be generated to one of the built-in types
# 4. name of the directory to save the data, 
# The file follow name convention: n<value>_<type>.in and n<value>_<type>.out
# The .in file is in the format:
# n
# target
# list of values
# The .out file is in the format:
# 1 or 0

import sys
import random
import os
import numpy as np

# generate only positive cases, the target is computed as the sum of a random subset
def generate_positive(num_files, n, data_type, directory=None):
    for i in range(num_files):   
        # arr values should be sample from a range of 1 to 1000 from binomial distribution
        arr = np.random.binomial(100, 0.1, n)
        # Probability distribution
        p = [0.8, 0.2]  # p(0)=0.8, p(1)=0.2
        # Generate a random vector of 0s and 1s
        random_vector = np.random.choice([0, 1], size=n, p=p)

        target = arr.dot(random_vector)
        target = target.tolist()
        with open(f"{f'{directory}/n{n}_{data_type}_{i}.in' if directory else f'n{n}_{data_type}_{i}.in'}", "w") as f:
            f.write(f"{n}\n{target}\n")
            f.write(" ".join(map(str, arr)))
        with open(f"{f'{directory}/n{n}_{data_type}_{i}.out' if directory else f'n{n}_{data_type}_{i}.out'}", "w") as f:
            f.write("1")

# generate only negative cases, the target is a random number that is not in the array or is a sum of a subset
def generate_negative(num_files, n, data_type, directory=None):
    for i in range(num_files):
        arr = np.random.binomial(100, 0.1, n)
        target = np.random.randint(10000)
        while target in arr and isSum(arr, target, n):
            target = np.random.randint(10000)
        with open(f"{f'{directory}/n{n}_{data_type}_{i}.in' if directory else f'n{n}_{data_type}_{i}.in'}", "w") as f:
            f.write(f"{n}\n{target}\n")
            f.write(" ".join(map(str, arr)))
        with open(f"{f'{directory}/n{n}_{data_type}_{i}.out' if directory else f'n{n}_{data_type}_{i}.out'}", "w") as f:
            f.write("0")


def isSum(arr, number, n):
    for i in range(0, n, 1):
        for j in range(0, n, 1):
            if number == sum(arr[i:j]):
                return True
    return False



if __name__ == "__main__":
    num_files = int(sys.argv[1])
    n = int(sys.argv[2])
    data_type = sys.argv[3]
    directory = sys.argv[4] if len(sys.argv) > 4 else None
    # Create the directory if it doesn't exist
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    if data_type == "positive":
        generate_positive(num_files, n, data_type, directory)
    elif data_type == "negative":
        generate_negative(num_files, n, data_type, directory)