text = """new unicode characters usually not installed but looks like something else
unicode grid to qr code
hentaigana
unicode character categories
"""
rows = ["qwfpgjluy", "arstdhneio", "zxcvbkm", "1234567890"]

for idx, line in enumerate(text.splitlines()):
    idx += 1
    if line[0] == ">":
        line = line[1:]
        line = "".join(chr(ord(i) + idx) for i in line)
    else:
        for row in rows:
            trans = str.maketrans(row, row[idx:] + row[:idx])
            line = line.translate(trans)
    print(line)