import struct, sys

def boxes(buf, start, end):
    off = start
    while off + 8 <= end:
        size = struct.unpack('>I', buf[off:off+4])[0]
        typ = buf[off+4:off+8].decode('latin1')
        if size == 1:
            size = struct.unpack('>Q', buf[off+8:off+16])[0]
            hdr = 16
        elif size == 0:
            size = end - off
            hdr = 8
        else:
            hdr = 8
        if size <= 0 or off + size > end:
            break
        yield typ, off + hdr, off + size
        off += size

def find(buf, start, end, path):
    if not path:
        yield (start, end)
        return
    for typ, cs, ce in boxes(buf, start, end):
        if typ == path[0]:
            for r in find(buf, cs, ce, path[1:]):
                yield r

def main(path):
    buf = open(path, 'rb').read()
    print('file: %s bytes=%d' % (path, len(buf)))
    for ms, me in find(buf, 0, len(buf), ['moov', 'mvhd']):
        v = buf[ms]
        if v == 0:
            ts = struct.unpack('>I', buf[ms+12:ms+16])[0]
            dur = struct.unpack('>I', buf[ms+16:ms+20])[0]
        else:
            ts = struct.unpack('>I', buf[ms+20:ms+24])[0]
            dur = struct.unpack('>Q', buf[ms+24:ms+32])[0]
        print('mvhd version=%d timescale=%d duration=%d seconds=%.3f' % (v, ts, dur, dur / ts if ts else -1))
    for ts_, te in find(buf, 0, len(buf), ['moov', 'trak']):
        w = h = None
        hdlr = None
        for hs, he in find(buf, ts_, te, ['mdia', 'hdlr']):
            hdlr = buf[hs+8:hs+12].decode('latin1')
        for ks, ke in find(buf, ts_, te, ['tkhd']):
            v = buf[ks]
            base = ks + (76 if v == 0 else 88)
            w = struct.unpack('>I', buf[base:base+4])[0] >> 16
            h = struct.unpack('>I', buf[base+4:base+8])[0] >> 16
        dur = None
        for ds, de in find(buf, ts_, te, ['mdia', 'mdhd']):
            v = buf[ds]
            if v == 0:
                tsc = struct.unpack('>I', buf[ds+12:ds+16])[0]
                dd = struct.unpack('>I', buf[ds+16:ds+20])[0]
            else:
                tsc = struct.unpack('>I', buf[ds+20:ds+24])[0]
                dd = struct.unpack('>Q', buf[ds+24:ds+32])[0]
            dur = dd / tsc if tsc else -1
        print('trak handler=%s width=%s height=%s duration_s=%s' % (hdlr, w, h, ('%.3f' % dur) if dur is not None else None))

if __name__ == '__main__':
    main(sys.argv[1])
