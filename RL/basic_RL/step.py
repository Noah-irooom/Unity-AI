def stepp(dp, s):
    if s[0] == 10: return 1.0
    if s[1] == 10: return 0.0
    if s in dp: return dp[s]
    dp[s] = (2*stepp(dp, (s[0]+1, s[1]))+ stepp(dp, s[0], s[1]+1))
