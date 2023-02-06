
def anded(strs):
    return word_listed(strs, 'and')

def ored(strs):
    return word_listed(strs, 'or')

def word_listed(strs, joiner):
    strs = list(strs)
    if len(strs) == 1:
        return strs[0]
    else:
        return f"{', '.join(strs[:-1])} {joiner} {strs[-1]}"
