import IO

def is_subset_sum(arr, target):
    n = len(arr)
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

S, t = IO.get_data()

if is_subset_sum(S, t):
    print("1")
else:
    print("0")