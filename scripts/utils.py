
def split_with_indices(s: str, sep=' '):
    parts = s.split(sep)
    res = [(0, parts[0])]

    for i in range(1, len(parts)):
        idx, word = res[i - 1]
        res.append((idx + len(word) + len(sep), parts[i]))

    return res
