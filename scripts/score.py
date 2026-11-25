"""Recalculate the assignment's nine equal-width interval scores transparently."""
import json, math
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def score(value,minimum,maximum,direction):
    value,minimum,maximum=map(lambda x:Decimal(str(x)),(value,minimum,maximum))
    if maximum<=minimum: raise ValueError('Reference range must be positive')
    z=(value-minimum)/(maximum-minimum) if direction=='higher' else (maximum-value)/(maximum-minimum)
    return min(9,max(1,int((9*z).to_integral_value(rounding=ROUND_CEILING))))

def main():
    path=ROOT/'data/indicators.json';bundle=json.loads(path.read_text(encoding='utf-8'))
    for r in bundle['indicators']:
        b=r.get('benchmark')
        r['scores']={'taiwan':None,'china':None}
        if not r['eligible'] or not b:continue
        observations=b['observations']
        if len(observations)!=b['n']:raise ValueError(f"{r['id']}: reference sample length mismatch {len(observations)} != {b['n']}")
        values=[x['value'] for x in observations]
        assert math.isclose(min(values),b['min'],rel_tol=1e-8,abs_tol=1e-8),r['id']
        assert math.isclose(max(values),b['max'],rel_tol=1e-8,abs_tol=1e-8),r['id']
        assert r['direction'] in ['higher','lower'],r['id']
        for country in ['taiwan','china']:
            r['scores'][country]=score(r[country]['value'],b['min'],b['max'],r['direction'])
    path.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Scored',sum(r['scores']['taiwan'] is not None for r in bundle['indicators']),'of 28 criteria')

if __name__=='__main__':main()
