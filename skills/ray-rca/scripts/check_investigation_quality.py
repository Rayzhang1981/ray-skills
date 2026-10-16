# -*- coding: utf-8 -*-
"""Structured review gate, not an automated scientific truth detector."""
import argparse
import copy
import json
from pathlib import Path
import sys


def _console_safe():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors='replace')
        except (AttributeError, ValueError):
            pass


_console_safe()
ROOT = Path(__file__).resolve().parents[1]


def validate_case(case):
    if not isinstance(case, dict):
        return ['invalid_schema']
    errors = set()
    records = case.get('records')
    conclusions = case.get('conclusions')
    if not isinstance(records, list) or not isinstance(conclusions, list) or not records or not conclusions:
        return ['empty_or_invalid_review']
    if any(not isinstance(r, dict) or not r.get('claim_id') for r in records + conclusions):
        return ['invalid_schema']
    ids = [r['claim_id'] for r in records]
    if len(set(ids)) != len(ids):
        errors.add('duplicate_evidence_id')
    by_id = {r['claim_id']: r for r in records}
    hypotheses = case.get('hypotheses', [])
    if not isinstance(hypotheses, list) or len(set(hypotheses)) < 2:
        errors.add('missing_competing_hypotheses')
    for c in conclusions:
        status = c.get('status')
        if status not in ('pending', 'conditional', 'confirmed', 'excluded', 'withdrawn'):
            errors.add('invalid_status')
        basis = c.get('basis')
        if not isinstance(basis, list) or not basis:
            errors.add('missing_evidence_basis')
            basis = []
        if any(cid not in by_id for cid in basis):
            errors.add('unknown_evidence_reference')
        if status in ('conditional', 'confirmed', 'excluded'):
            for field in ('model_applicability', 'input_basis', 'scope'):
                if not isinstance(c.get(field), str) or not c[field].strip():
                    errors.add('missing_' + field)
        if status in ('confirmed', 'excluded'):
            if c.get('model_verified') is not True:
                errors.add('model_not_verified')
            if c.get('input_basis_verified') is not True:
                errors.add('input_basis_not_verified')
            if c.get('alternatives_reviewed') is not True:
                errors.add('alternatives_not_reviewed')
            if c.get('independent_evidence') is not True:
                errors.add('no_independent_evidence')
            if any(by_id[cid].get('evidence_level') in ('Hypothesis', 'Assumption') or by_id[cid].get('verified') is not True for cid in basis if cid in by_id):
                errors.add('unsupported_promotion')
    return sorted(errors)


def selftest():
    data = json.loads((ROOT / 'tests' / 'investigation_cases.json').read_text(encoding='utf-8'))
    cases = data.get('cases', [])
    if not cases:
        raise ValueError('empty test suite')
    failed = []
    for case in cases:
        actual = validate_case(case['review'])
        expected = sorted(case['expected_errors'])
        good = actual == expected
        print('[%s] %s actual=%s expected=%s' % ('PASS' if good else 'FAIL', case['id'], actual, expected))
        if not good:
            failed.append(case['id'])
    positive = copy.deepcopy(cases[0]['review'])
    positive['conclusions'][0]['model_applicability'] = ''
    good = validate_case(positive) == ['missing_model_applicability']
    print('[%s] mutation-delete-model-field' % ('PASS' if good else 'FAIL'))
    if not good:
        failed.append('mutation-delete-model-field')
    print('RULE TESTS: %d/%d; does not verify evidence truth or model physics.' % (len(cases)+1-len(failed), len(cases)+1))
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--input', type=Path)
    args = ap.parse_args()
    if args.input:
        result = validate_case(json.loads(args.input.read_text(encoding='utf-8')))
        print(json.dumps({'errors': result, 'structural_review_only': True}, ensure_ascii=True))
        return 1 if result else 0
    return selftest()


if __name__ == '__main__':
    raise SystemExit(main())
