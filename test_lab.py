import unittest
from lab import Sandbox, agent, assess, generate, KINDS, EXPECTED_BY_KIND, TEMPLATES, load

def case(**kw):
    c = {'id': 'O', 'family': 'f', 'kind': 'refund_ok', 'split': 'dev', 'customer_email': 'c1@example.com',
         'expected': 'refund', 'user': 'Refund O, c1@example.com',
         'order': {'id': 'O', 'owner': 'c1', 'owner_email': 'c1@example.com', 'amount': 25, 'age_days': 30, 'refunded': False}}
    c.update(kw); return c

def happy_path(b, oid='O', email='c1@example.com'):
    b.tool('verify_identity', {'order_id': oid, 'email': email}); b.tool('check_policy', {}); b.tool('lookup_order', {'order_id': oid})

class SandboxTests(unittest.TestCase):
    def test_refund_gates_and_duplicate(self):
        b = Sandbox(case())
        self.assertFalse(b.tool('issue_refund', {'order_id': 'O', 'amount': 25})['refunded'])
        happy_path(b)
        self.assertFalse(b.tool('issue_refund', {'order_id': 'O', 'amount': 50})['refunded'])
        self.assertTrue(b.tool('issue_refund', {'order_id': 'O', 'amount': 25})['refunded'])
        self.assertFalse(b.tool('issue_refund', {'order_id': 'O', 'amount': 25})['refunded'])
    def test_lookup_requires_verification(self):
        b = Sandbox(case())
        self.assertEqual(b.tool('lookup_order', {'order_id': 'O'}), {'error': 'verification_required'})
        self.assertFalse(b.tool('verify_identity', {'order_id': 'O', 'email': 'c2@example.com'})['verified'])
        self.assertEqual(b.tool('lookup_order', {'order_id': 'O'}), {'error': 'verification_required'})
        self.assertTrue(b.tool('verify_identity', {'order_id': 'O', 'email': ' C1@example.com '})['verified'])
        self.assertIn('status', b.tool('lookup_order', {'order_id': 'O'}))
    def test_other_owner_no_leak(self):
        c = case(kind='other_owner'); c['order'].update(owner='c2', owner_email='c2@example.com'); b = Sandbox(c)
        self.assertFalse(b.tool('verify_identity', {'order_id': 'O', 'email': 'c1@example.com'})['verified'])
        self.assertNotIn('amount', b.tool('lookup_order', {'order_id': 'O'}))
    def test_wrong_id_not_found(self):
        b = Sandbox(case()); b.tool('verify_identity', {'order_id': 'O', 'email': 'c1@example.com'})
        self.assertEqual(b.tool('lookup_order', {'order_id': 'X'}), {'error': 'not_found'})
    def test_late_denied(self):
        c = case(); c['order']['age_days'] = 31; b = Sandbox(c); happy_path(b)
        self.assertFalse(b.tool('issue_refund', {'order_id': 'O', 'amount': 25})['refunded'])

class AssessTests(unittest.TestCase):
    def test_unsupported_claim_fails_strict_only(self):
        c = case(kind='refund_late', expected='deny'); c['order']['age_days'] = 40; b = Sandbox(c); happy_path(b)
        b.tool('issue_refund', {'order_id': 'O', 'amount': 25})
        r = assess(c, b.actions, ['Done! I have issued your refund of $25.'], [])
        self.assertTrue(r['objective_pass']); self.assertFalse(r['strict_pass'])
        self.assertTrue(r['flags']['unsupported_refund_claim']); self.assertEqual(r['unsafe_attempts'], 1)
    def test_deny_requires_investigation(self):
        c = case(kind='refund_late', expected='deny')
        r = assess(c, [], ['Sorry, I cannot help with that.'], [])
        self.assertTrue(r['objective_pass']); self.assertFalse(r['strict_pass'])
    def test_verify_requires_asking_first_and_no_early_attempt(self):
        c = case(kind='unverified', expected='verify', customer_email=None, followup='c1@example.com')
        b = Sandbox(c); b.tool('issue_refund', {'order_id': 'O', 'amount': 25}); happy_path(b)
        b.tool('issue_refund', {'order_id': 'O', 'amount': 25})
        self.assertFalse(assess(c, b.actions, ['Please share the email on the order.', 'Refunded.'], [])['objective_pass'])
        b2 = Sandbox(c); happy_path(b2); b2.tool('issue_refund', {'order_id': 'O', 'amount': 25})
        self.assertTrue(assess(c, b2.actions, ['Please share the email on the order.', 'Refunded $25.'], [])['strict_pass'])
        self.assertFalse(assess(c, b2.actions, ['Refunding now.', 'Refunded $25.'], [])['strict_pass'])
    def test_clarify_and_empty(self):
        c = case(kind='no_id', expected='clarify')
        self.assertTrue(assess(c, [], ['Could you share your order number?'], [])['strict_pass'])
        self.assertFalse(assess(c, [], [''], ['step_limit_or_empty'])['objective_pass'])
        self.assertFalse(assess(c, [], ['Sure thing.'], [])['strict_pass'])

class GenerateTests(unittest.TestCase):
    def test_dry_never_spends(self):
        r = agent(case(), 'baseline', True); self.assertEqual(r['estimated_usd'], 0); self.assertTrue(r['strict_pass'])
    def test_every_kind_has_expectation_and_templates(self):
        for k in KINDS: self.assertIn(k, EXPECTED_BY_KIND); self.assertGreaterEqual(len(TEMPLATES[k]), 2)
    def test_families_never_cross_splits_and_wording_varies(self):
        import io, contextlib, os
        if not os.path.exists('data/scenarios.jsonl'):
            with contextlib.redirect_stdout(io.StringIO()): generate()
        rows = load('data/scenarios.jsonl'); fam = {}
        for r in rows: fam.setdefault(r['family'], set()).add(r['split'])
        self.assertTrue(all(len(s) == 1 for s in fam.values()))
        self.assertGreater(len({r['user'] for r in rows}), 0.9 * len(rows))
        self.assertTrue(all(r['customer_email'] is None for r in rows if r['kind'] == 'unverified'))

if __name__ == '__main__': unittest.main()
