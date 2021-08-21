text = """morse code in binary to hex feat. retro game explained video
same thing but in speech
pokémon gen 1 compression
multiplication table in na’vi
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