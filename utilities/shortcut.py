"""
Returns hit as the full string that the shortcut is for if it is able to resolve the shortcut
Returns empty string otherwise
The second return is "Y" if there was ambiguity in the shortcut
"""


def resolve_shortcut(string_list, shortcut):
    hit = ""  # The full string that was shortcut
    suspect = ""  # A suspected hit
    ambiguous = False  # Is the shortcut ambiguous?
    for candidate in string_list:
        if candidate.upper() == shortcut.upper():
            hit = candidate
        if candidate.upper().startswith(shortcut.upper()):
            if not suspect:
                suspect = candidate
            else:
                ambiguous = True

    if not hit and suspect and not ambiguous:
        hit = suspect

    return hit, ambiguous

# Exact match
assert resolve_shortcut("A,AA,B,C,D".split(","), "A") == ('A',True)

# Ambiguous
assert resolve_shortcut("AA1,AA2,B,C,D".split(","), "A") == ('', True)

# Not ambiguous, just a bad E
assert resolve_shortcut("AA1,AA2,B,C,D".split(","), "E") == ('',False)

# Normal use, shortcut to single name.
assert resolve_shortcut("AA1,AA2,BBB,C,D".split(","), "B") == ('BBB',False)
