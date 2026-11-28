"""Local-only integration of approved intents with the mock HTTP downstream.

This demonstration assumes one worker and a fixed loopback service; it is not production code.
"""
import hashlib


def dispatch(service, identity, operation_id, downstream, *, lose_response=False):
    claim = service.claim_external_submission(identity, operation_id)
    if not claim['claimed']:
        return {'state': claim['state'], 'receipt': claim['receipt']}
    payload = claim['payload']
    try:
        receipt = downstream.create(operation_id, payload, lose_response=lose_response)
    except TimeoutError:
        return {'state': 'unknown', 'receipt': None}
    digest = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    return service.confirm_external_submission(identity, operation_id, receipt, digest)


def reconcile(service, identity, operation_id, downstream):
    current = service.get_external_submission(identity, operation_id)
    if current['state'] == 'confirmed':
        return current
    if current['state'] != 'unknown':
        raise ValueError('only an unknown operation can be reconciled')
    try:
        found = downstream.lookup(operation_id)
    except TimeoutError:
        return current
    if found is None:
        return current
    return service.confirm_external_submission(identity, operation_id, found['receipt'], found['digest'])
