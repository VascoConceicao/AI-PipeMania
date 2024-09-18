def list_to_int(w, n) :
    res = 0
    for i in range(len(w)):
        res += w[-i - 1]*(n**i)
    return res

print([1 for i in range(64)])
i = list_to_int([11 for i in range(64)], 12)