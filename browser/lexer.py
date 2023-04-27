

class Text:
    def __init__(self, text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag


# Returns a list of tokens (Text or Tag objects) for the given text
def lex(body):
    out = []
    in_tag = False
    text = ""
    for c in body:
        if c == "<":
            in_tag = True
            if text:
                out.append(Text(text))
            text = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(text))
            text = ""
        else:
            text += c

    if not in_tag and text:
        out.append(Text(text))

    # TODO: replace character entities
    # for reserved, entity in ENTITIES.items():
    #     text = text.replace(entity, reserved)
    
    return out
