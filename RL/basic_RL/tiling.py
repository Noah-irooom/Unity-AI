def Tiling(n):
    if n == 1: return 1
    if n == 2: return 3
    return Tiling(n-1) + 2*Tiling(n-2)






n = int(input("n = "))
print(Tiling(n))
