"""Independent Census ZIP/binary-to-complete-derivative audit, no producer code."""
from pathlib import Path
from collections import Counter
import binascii
import gzip
import hashlib
import io
import json
import struct
import zipfile

S = Path(__file__).resolve().parents[1]
M = S / 'maps'
N = 0


def ck(ok, note=''):
    global N
    assert ok, note
    N += 1


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def main():
    path = M / 'receipts/census-vtd-zip.json'
    r = json.loads(path.read_bytes())
    ck(r['status'] == 200)
    hop = r['hops'][-1]
    parts = []
    pins = [pin(path)]
    for x in hop['stored_parts']:
        p = M / x['path']
        z = p.read_bytes()
        ck((len(z), sha(z)) == (x['bytes'], x['sha256']))
        ck(len(z) < 40000000)
        parts.append(z)
        pins.append(pin(p))
    raw = gzip.decompress(b''.join(parts))
    ck((len(raw), sha(raw)) == (hop['raw_bytes'], hop['raw_sha256']))
    z = zipfile.ZipFile(io.BytesIO(raw))
    members = []
    for item in z.infolist():
        b = z.read(item.filename)
        ck(len(b) == item.file_size and binascii.crc32(b) & 0xffffffff == item.CRC)
        members.append(dict(name=item.filename, bytes=len(b), sha256=sha(b), CRC32='%08x' % item.CRC))
    ck(len(members) == 7)
    stem = 'tl_2020_34_vtd20'
    shp, shx, dbf = [z.read(stem + '.' + ext) for ext in ['shp', 'shx', 'dbf']]
    encoding = z.read(stem + '.cpg').decode().strip()
    for b in [shp, shx]:
        ck(struct.unpack_from('>i', b)[0] == 9994)
        ck(struct.unpack_from('>i', b, 24)[0] * 2 == len(b))
        ck(struct.unpack_from('<2i', b, 28) == (1000, 5))
    ck(shp[36:100] == shx[36:100])
    count = struct.unpack_from('<I', dbf, 4)[0]
    hlen, rlen = struct.unpack_from('<2H', dbf, 8)
    ck(count == 6361 and len(shx) == 100 + 8 * count)
    fields = []
    k = 32
    while dbf[k] != 13:
        b = dbf[k:k + 32]
        fields.append(dict(name=b[:11].split(b'\0')[0].decode('ascii'), type=chr(b[11]), size=b[16], decimal=b[17]))
        k += 32
    ck(k + 1 == hlen and sum(f['size'] for f in fields) + 1 == rlen)
    derivative = M / 'derived/census-vtd-native.jsonl.gz'
    pins.append(pin(derivative))
    offset = 100
    xyhash = hashlib.sha256()
    rows = []
    counties = Counter()
    pointcount = partcount = 0
    with gzip.open(derivative, 'rt') as stream:
        for i, line in enumerate(stream):
            obj = json.loads(line)
            ck(i < count and obj['index'] == i)
            recno, words = struct.unpack_from('>2i', shp, offset)
            ck((recno, words) == (i + 1, struct.unpack_from('>2i', shx, 100 + 8 * i)[1]))
            ck(struct.unpack_from('>i', shx, 100 + 8 * i)[0] * 2 == offset)
            payload = shp[offset + 8:offset + 8 + words * 2]
            ck(struct.unpack_from('<i', payload)[0] == 5)
            rings, points = struct.unpack_from('<2i', payload, 36)
            parts = list(struct.unpack_from('<%di' % rings, payload, 44))
            xy = payload[44 + 4 * rings:]
            geom = obj['geometry']
            ck(len(xy) == 16 * points)
            ck(geom['shape_type'] == 5 and geom['parts'] == parts)
            ck(struct.pack('<4d', *geom['bbox']) == payload[4:36])
            ck(len(geom['points']) == points)
            for p, expected in zip(geom['points'], struct.iter_unpack('<2d', xy)):
                ck(struct.pack('<2d', *p) == struct.pack('<2d', *expected))
            xyhash.update(xy)
            row = dbf[hlen + i * rlen:hlen + (i + 1) * rlen]
            ck(len(row) == rlen and obj['deletion_flag_hex'] == row[:1].hex())
            pos = 1
            attrs = {}
            cells = []
            for f in fields:
                b = row[pos:pos + f['size']]
                pos += f['size']
                cells.append(b.hex())
                if f['type'] == 'C':
                    value = b.decode(encoding).strip().rstrip('\0')
                elif f['type'] == 'N':
                    value = (int(b.strip()) if f['decimal'] == 0 else float(b.strip())) if b.strip() else None
                else:
                    raise AssertionError(('unhandled literal DBF field', f))
                attrs[f['name']] = value
            ck(obj['raw_dbf_cells_hex'] == cells and obj['attributes'] == attrs)
            counties[attrs['COUNTYFP20']] += 1
            rows.append(dict(record=i, SHP_offset=offset, content_words=words, raw_SHP_sha256=sha(payload), raw_DBF_sha256=sha(row)))
            pointcount += points
            partcount += rings
            offset += 8 + len(payload)
    ck(len(rows) == count and offset == len(shp) and len(counties) == 21)
    ck(pointcount == 2302234)
    result = dict(status='pass_independent_complete_Census_binary_original_review', checks=N,
                  complete_original_pins=pins, complete_ZIP_members=members, records=count,
                  all21_county_counts=dict(sorted(counties.items())), native_XY_positions=pointcount,
                  ring_parts=partcount, original_XY_IEEE754_bytes_sha256=xyhash.hexdigest(),
                  every_record=rows, complete_DBF_schema=fields, encoding=encoding,
                  raw_PRJ=z.read(stem + '.prj').decode(),
                  producer_imports_or_writes=False, coordinate_or_part_repair=False,
                  qualification='Historical Census2020 VTD source only. Every original ZIP member, binary record/index offset, DBF raw cell and complete derivative XY bit/part/bbox checked independently with stdlib; no geometry adapter, legal/topology/current/source-label match or vote allocation claim.')
    out = S / 'data/coordinator-census-map-original-review.json'
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(checks=N, records=count, points=pointcount, parts=partcount, output=pin(out))))


if __name__ == '__main__':
    main()
