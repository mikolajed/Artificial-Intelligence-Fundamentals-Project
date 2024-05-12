def is_subset_sum(arr, n, target):
    # Base cases
    if target == 0:
        return True
    if n == 0 and target != 0:
        return False

    # If last element is greater than target, ignore it
    if arr[n-1] > target:
        return is_subset_sum(arr, n-1, target)

    # Check if sum can be obtained by including or excluding the last element
    return is_subset_sum(arr, n-1, target) or is_subset_sum(arr, n-1, target-arr[n-1])

# Get data from the console
n = int(input())        # Number of elements in the list
target = int(input())   # Target sum

arr = [int(x) for x in input().split(' ')]   # List of values

if is_subset_sum(arr, n, target):
    print("1")
else:
    print("0")