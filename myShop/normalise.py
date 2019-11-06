import string

def remove_punct(text):
    for punc in string.punctuation:
        text = text.replace(punc, '')

    return text

def remove_spaces(text):
    space_remove = text.strip()
    extra_space_remove = space_remove.replace("   ", "  ")
    return extra_space_remove

def normalise_input(user_search):
    punct_removed = remove_punct(user_search).lower()
    space_removed = remove_spaces(punct_removed)

    return space_removed