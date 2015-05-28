def slash(string):
    if string[-1] != '/':
        string+='/'
    while (string[-2:] == "//"):
        string=string[:-1]

    return string
