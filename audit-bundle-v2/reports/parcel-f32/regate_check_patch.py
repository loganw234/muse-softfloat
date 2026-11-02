import pathlib
a=pathlib.Path('worktrees/w1-f32/tests/gen_vectors_f32.py').read_bytes().replace(b'\r\n',b'\n')
b=pathlib.Path('scratch/parcel-f32/patched_gen.py').read_bytes().replace(b'\r\n',b'\n')
print('identical to pre-validated patched_gen:', a==b, len(a), len(b))
