import IO

def ssp_fptas_binary(S, t, epsilon):
    n = len(S)
    s_max = max(S)
    K = epsilon * s_max / n

    scaled_S = [int(s / K) for s in S]
    scaled_t = int(t / K)
    scaled_t_approx = int((1 + epsilon) * t / K)

    max_sum = sum(scaled_S)
    dp = [False] * (max_sum + 1)
    dp[0] = True

    for num in scaled_S:
        for j in range(max_sum, num - 1, -1):
            if dp[j - num]:
                dp[j] = 1

    for j in range(scaled_t_approx + 1):
        if dp[j]:
            return 1

    return 0

S, t = IO.get_data()

epsilon = 0.1

print(ssp_fptas_binary(S, t, epsilon))  # Output: True or False
