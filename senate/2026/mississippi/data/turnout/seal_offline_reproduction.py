"""Pin a completed offline rebuild without hashing validation or its manifest."""
import json

from acquire_sources import BASE, OUT, savejson, sha


def main():
    log=OUT/'qa/reproduction-final-scope-v3-2026-10-19.log'
    raw=log.read_bytes()
    lines=raw.decode(errors='replace').splitlines()
    assert lines[-1].startswith('{"status": "pass_offline_qa_qualified_pending_coordinator_acceptance"')
    assert '"failed_or_pending_checks": []' in lines[-1]
    assert lines[-2].startswith('Manifest verified: ')
    targets={
        'builder':OUT/'build_all.py',
        'report':BASE/'turnout.md',
        'county_csv':BASE/'data/county-turnout.csv',
        'native_priority_contract':OUT/'priority-set.json',
        'complete_2024_all11_source_dependency':OUT/'source/2024-preferred-all11-source-fields-v1.json.gz',
        'complete_historical_native_dependencies':OUT/'historical-native-complete-dependencies.json',
        'source_schema':OUT/'source/SCHEMA.md',
    }
    pins={name:{'path':str(path.relative_to(BASE)),'bytes':path.stat().st_size,
                'sha256':sha(path.read_bytes())} for name,path in targets.items()}
    contract=json.loads(targets['native_priority_contract'].read_text())
    assert len(contract['all_unit_order'])==1736 and len(contract['ordered_priority_keys'])==887
    assert contract['historical_source_native_dependencies']['full_peer_source_objects_canonical'] is True
    assert contract['peer_agreement']['complete_independent_native_priority_v2']['all11_candidate_or_null_positions']==24926
    receipt={
        'schema':'offline_reproduction_completion_v1',
        'command':'PYTHONDONTWRITEBYTECODE=1 python senate/2026/mississippi/data/turnout/build_all.py',
        'process_exit_code':0,
        'completed_log':{'path':str(log.relative_to(BASE)),'bytes':len(raw),'sha256':sha(raw)},
        'final_line':lines[-1],
        'output_pins':pins,
        'qualified_scope':'Complete 2024 preferred named candidate source fields and native order; exact frozen 2020/2018 canonical source dependencies; bounded own historical native replay. No current 2026 geographic or coordinator acceptance.',
    }
    savejson(OUT/'qa/final-offline-reproduction.json',receipt)
    print('Sealed completed offline rebuild',len(raw),sha(raw))


if __name__=='__main__':main()
