#!/usr/bin/env python3
"""Generates the F-02 (exponent clamp) and F-13 (beyond-20-digit) inputs used in the audit.
Usage: python3 make_cases.py   -> writes st1.txt (F-02 cases, one per line, expected answers in st1.labels)
                                   and st2.txt (F-13: 55-digit exact expansion of the double 0.1).
Then:  gcc -std=c11 -O2 -Iinclude src/msf*.c st/drv.c -o drv && ./drv 0 < st1.txt   (arg = rounding mode 0..4)"""
from decimal import Decimal, getcontext
getcontext().prec = 100
cases = [
 ("control: 1 + 1000 zeros e-1000 (=1.0)",           "1"+"0"*1000+"e-1000",           "3ff0000000000000 00"),
 ("F-02: 1 + 100001 zeros e-100002 (=0.1)",           "1"+"0"*100001+"e-100002",        "3fb999999999999a 10"),
 ("F-02: 1 + 200000 zeros e-200000 (=1.0)",           "1"+"0"*200000+"e-200000",        "3ff0000000000000 00"),
 ("F-02: 0. + 200000 zeros + 1e200001 (=1.0)",        "0."+"0"*200000+"1e200001",       "3ff0000000000000 00"),
]
open("st1.txt","w").write("".join(s+"\n" for _,s,_ in cases))
open("st1.labels","w").write("".join(f"{l} | exact answer: {w}\n" for l,_,w in cases))
open("st2.txt","w").write(str(Decimal(0.1))+"\n")   # exactly representable; correct = 3fb999999999999a, flags 00, every mode
