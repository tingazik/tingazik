# pip3 install morse3
from typing import List
from morse3 import Morse as m

def transform(seq: str) -> List[bool]:
    morse_s_seq: str = m(seq).stringToMorse()
    morse_seq = ""
    for i in morse_s_seq:
        morse_seq += i + " "
    morse_seq.replace("      ", "       ")
    result: List[bool] = []
    for i in morse_seq:
        if i == ".":
            result.append(True)
        elif i == "-":
            result.extend([True, True, True])
        elif i == " ":
            result.append(" ")
        else:
            raise Exception(f"Unknown character '{i}'")

# sample rate: 23301.689 smp/s