import sys
print(sys.version)
try:
    import mpmath
    print("mpmath", mpmath.__version__)
except ImportError as e:
    print("NO mpmath:", e)
