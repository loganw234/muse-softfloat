import tarfile, sys
tf = tarfile.open(sys.argv[1], 'r:gz')
for m in tf.getmembers():
    if 'changelog' in m.name.lower():
        print(m.name, 'type=', m.type, 'linkname=', repr(m.linkname))
