from browser.constants import ENTITIES


# Returns all non-tag text, replacing entities with their corresponding symbols
def lex(body):
    in_angle = False
    content = ""
    for c in body:
        if c == "<":
            in_angle = True
        elif c == ">":
            in_angle = False
        elif not in_angle:
            content += c

    for reserved, entity in ENTITIES.items():
        content = content.replace(entity, reserved)
    
    return content
