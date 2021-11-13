# 비재귀적 프로그래밍
def forward_fib(n):
    f = [0, 1]
    for _ in range(2, n+1, 2):
        f[0] += f[1]
        f[1] += f[0]
    return f[n%2]

# 재귀적 프로그래밍
def recursive_fib(n):
    if n == 0: return 0
    if n == 1: return 1
    return recursive_fib(n-1) + recursive_fib(n-2)

# 동적 프로그래밍 Memoism
def fib(dp, n):
    if n == 0: return 0
    if n == 1: return 1
    if n in dp: return dp[n]
    dp[n] = fib(dp, n-1) + fib(dp, n-2)
    return dp[n]

# 수학적 접근 방법
import math
Sqrt5 = math.sqrt(5)
Phi = (1+Sqrt5)/2

def math_fib(n):
    return int((Phi**n - (1-Phi)**n)/Sqrt5 + 0.5)

dp = dict() #메모리에 저장하고 불러오는 식으로 활용 - 기존 재귀법 보다 빠
n = int(input("n = "))
# print(fib(dp, n))
print(math_fib(n))
