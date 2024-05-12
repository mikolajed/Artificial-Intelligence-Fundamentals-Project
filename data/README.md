# About the scripts and data format

## Tools
File `generate.py` allows for generating data for the SSP. It takes the following command line arguments:
1. k - the number of files to generate
2. n - the size of the list in SSP
3. type - the type of the data to generate, supports types: positive, TODO MORE
4. dir_out - the directory where to output the files

## Input files
Files are split into .in and .out corresponding to the input and output data. 
The .in file is in format
```
n
target
list_of_values
```

### Example:
```
10
6
1 1 3 2 8 4 5 9 12 99
```

## Output files
The .out file is just a single character 1 or 0.