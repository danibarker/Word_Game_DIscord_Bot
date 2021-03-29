

def break_message_into_pieces(s,LIMIT=1500):
    if len(s) <= LIMIT:
        yield s
    else:
        quoted = False
        if s.startswith("```") and s.endswith("```"):
            s = s[3:-3]
            quoted = True
            LIMIT = LIMIT - len("```")*2
        
        lines = s.split("\n")
        total = 0
        batch = []
        for line in lines:
            # Count the length of the lines plus the newlines between.
            if total + len(line) + len(batch)-1 <= LIMIT:
                total += len(line)
                batch.append(line)
            else:
                msg = '\n'.join(batch)
                if quoted:
                    yield '```' + msg + '```'
                else:
                    yield msg
                    
                # Reset for the next batch.
                batch = [line]
                total = len(line)
                
        if batch:
            # Don't forget the last batch.
            msg = '\n'.join(batch)
            if quoted:
                yield '```' + msg + '```'
            else:
                yield msg
                
# Put in some tests that make sure the code above is running properly.
# When the code above is changed (correctly), the following tests should still pass:

xs = list(break_message_into_pieces("one\ntwo\nthree\nfour\nfive\nsix\nseven",10))
assert xs == ['one\ntwo', 'three\nfour', 'five\nsix', 'seven']

xs = list(break_message_into_pieces("```one\ntwo\nthree\nfour\nfive\nsix\nseven```",10))
assert xs == ['```one```', '```two```', '```three```', '```four```', '```five```', '```six```', '```seven```']

xs = list(break_message_into_pieces("```one\ntwo\nthree\nfour\nfive\nsix\nseven```",20))
assert xs == ['```one\ntwo\nthree```', '```four\nfive\nsix```', '```seven```']




