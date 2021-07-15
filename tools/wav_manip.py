#%% pip3 install bitstring

# <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US" xmlns:mstts="https://www.w3.org/2001/mstts">
# <voice name="en-US-AriaNeural">
# <mstts:express-as style="chat">
# <prosody rate="-10.00%" volume="+50.00%">incomprehensible</prosody>
# </mstts:express-as>
# </voice>
# </speak>

# spx synthesize --file text.ssml --audio output canyourepeat.wav
# ffmpeg -i canyourepeat.wav -c:a pcm_u8 -ar 8000 repeat.wav

import io
import struct
base = "/Users/blueset/Downloads/morse"
f = open(base + ".wav", "rb").read()
bio = io.BytesIO(f)
# %%
bio.seek(0)
if bio.read(4) != b'RIFF':
    raise Exception("Unknown format")
# %%
bio.seek(4 * 3)

while bio.read(4) != b'fmt ':
    skip = struct.unpack("I", bio.read(4))[0]
    print("skip", skip)
    bio.seek(skip, 1)

fmt_chunk_size = sample_rate = struct.unpack("I", bio.read(4))[0]
bio.seek(2+2, 1)
sample_rate = struct.unpack("I", bio.read(4))[0]
print(sample_rate, "Hz")
bio.seek(4+2, 1)
bit_size = struct.unpack("H", bio.read(2))[0]
byte_size = bit_size // 8
byte_type = " BH I   Q"[byte_size]
sep = 1 << (bit_size - 1)
top = (sep << 1) - 1
bio.seek(fmt_chunk_size - (2+2+4+4+2+2), 1)
print(bit_size, byte_size, byte_type, sep, top)

while bio.read(4) != b'data':
    skip = struct.unpack("I", bio.read(4))[0]
    print("skip", skip)
    bio.seek(skip, 1)
# %%
question = ""
chunk_size = struct.unpack("I", bio.read(4))[0]
offset = 0
while offset < chunk_size:
    val = struct.unpack(byte_type, bio.read(byte_size))[0]
    write = 0
    if val > sep:
        write = (sep << 1) - 1
    bio.seek(-byte_size, 1)
    bio.write(struct.pack(byte_type, write))
    question += "1" if write else "0"
    offset += byte_size

#%%
with open(base + "_polarize.wav", "wb") as f:
    bio.seek(0)
    f.write(bio.read())
# %%
question = question.strip("0")
if len(question) % 8 != 0:
     missing = 8 - len(question) % 8
     question += "0" * missing

print(len(question) / sample_rate)
from bitstring import BitArray
import textwrap
print(textwrap.fill(BitArray(bin=question).hex))
