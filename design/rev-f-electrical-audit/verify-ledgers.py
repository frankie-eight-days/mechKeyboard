"""Check the published Rev F ledgers against a KiCad XML export, or the archived review ZIP."""
import argparse
import csv
from collections import Counter
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile

base = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('export', type=Path, nargs='?', default=base.parent / 'prelayout-review-evidence.zip')
source = parser.parse_args().export
if source.suffix == '.zip':
    with ZipFile(source) as z:
        xml = ET.fromstring(z.read('exports/net.xml'))
else:
    xml = ET.parse(source).getroot()


def load(name):
    with (base / (name + '.csv')).open() as f:
        return list(csv.DictReader(f))


def require(predicate, message):
    if not predicate:
        raise ValueError(message)


refs = {c.get('ref') for c in xml.findall('components/comp')}
nets = {(p.get('ref'), p.get('pin')): n.get('name') for n in xml.findall('nets/net') for p in n.findall('node')}
require(Counter(r['ref'] for r in load('references')) == Counter(refs), 'reference population differs')
require({(r['ref'], r['pin']): r['net'] for r in load('pins')} == nets, 'pin map differs')
for name, pattern, count in [('capacitors', r'C\d+', 122), ('resistors-inductors', r'(?:R|RV|L)\d+', 73)]:
    rows = load(name)
    require(len(rows) == count and Counter(r['ref'] for r in rows) == Counter(r for r in refs if re.fullmatch(pattern, r)), name + ' references differ')
    for r in rows:
        for pin, field in [('1','pad_1_net'), ('2','pad_2_net'), ('3','pad_3_net'), ('MP','mount_net')]:
            if r.get(field):
                require(nets.get((r['ref'],pin)) == r[field], f"{r['ref']}.{pin} differs")
for r in load('capacitors'):
    require(r['technology'] and abs(float(r['rated_v']) - float(r['extended_screen_abs_delta_v']) - float(r['rated_minus_screen_v'])) < .002, r['ref'] + ' margin differs')
semi = load('semiconductors')
physical = {r for r in refs if re.fullmatch(r'(?:D|Q|LED)\d+',r)} | {'U201','U202'}
expected = {r: 2 if r in {'D800','D801','U201','U202'} else 1 for r in physical}
require(Counter(r['reference'] for r in semi if r['reference'] in physical) == expected, 'semiconductor population differs')
supply = load('supply-pins')
for r in supply:
    require(nets.get((r['ref'],r['pin'])) == r['net'], f"{r['ref']}.{r['pin']} rail differs")
require({r['ref'] for r in supply if r['ref'].startswith('U')} == {r for r in refs if r.startswith('U')}, 'IC supply/return coverage differs')
logic = load('logic-levels')
ends = {r[col] for r in logic for col in ('driver_pin','receiver_pin')}
wanted = set()
for n in xml.findall('nets/net'):
    for p in n.findall('node'):
        typ = p.get('pintype','')
        if p.get('ref').startswith(('U','Q','LED','J200')) and not n.get('name').startswith('unconnected-') and '+no_connect' not in typ and typ.split('+')[0] in ('input','output','bidirectional','open_collector'):
            wanted.add(p.get('ref') + ':' + p.get('pin'))
require(wanted <= ends, f'logic endpoints missing {wanted - ends}')
identities = {(r['id'],r['driver_pin'],r['receiver_pin'],r['state'],r['path']) for r in logic}
require(len(identities) == len(logic), 'duplicate logic case')
for r in logic:
    if ':' in r['receiver_pin']:
        pair = tuple(r['receiver_pin'].split(':',1))
        if pair in nets:
            require(nets[pair] == r['net_at_receiver'],r['receiver_pin']+' receiver net differs')
    for a,b,c in [('VOH_min_V','VIH_min_V','high_margin_V'),('VIL_max_V','VOL_max_V','low_margin_V')]:
        if r[c]:
            require(abs(float(r[a])-float(r[b])-float(r[c])) < .00001,r['id']+' logic arithmetic differs')
require(Counter(r['id'] for r in logic)['MAT-H'] == 67 and Counter(r['id'] for r in logic)['PIX-HOP'] == 66,'missing key or pixel path')
print(f'{len(refs)} refs, {len(nets)} pins; 122 C, 73 R/RV/L; {len(physical)} fitted semiconductor refs; {len(supply)} supply/return case rows; {len(logic)} logic cases, {len(wanted)} declared signal pins. Inventory, covered terminal names and numeric arithmetic matched.')
