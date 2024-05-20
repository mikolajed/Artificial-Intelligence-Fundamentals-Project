def get_data():
    n = int(input())   # Number of elements in the list
    t = int(input())   # Target sum

    S = [int(x) for x in input().split(' ')]   # List of values

    return S, t