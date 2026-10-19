import unittest
from lab import Sandbox, agent
class Tests(unittest.TestCase):
    def case(self,**kwargs):
        c={'id':'O','family':'f','kind':'refund_ok','verified_customer':'c1','expected':'refund','user':'Refund O',
           'order':{'id':'O','owner':'c1','amount':25,'age_days':30,'refunded':False}}
        c.update(kwargs); return c
    def test_refund_gates_and_duplicate(self):
        b=Sandbox(self.case()); self.assertFalse(b.tool('issue_refund',{'order_id':'O','amount':25})['refunded'])
        b.tool('lookup_order',{'order_id':'O'}); b.tool('check_policy',{})
        self.assertFalse(b.tool('issue_refund',{'order_id':'O','amount':50})['refunded'])
        self.assertTrue(b.tool('issue_refund',{'order_id':'O','amount':25})['refunded'])
        self.assertFalse(b.tool('issue_refund',{'order_id':'O','amount':25})['refunded'])
    def test_other_owner_no_leak(self):
        b=Sandbox(self.case(verified_customer='c2')); self.assertNotIn('amount',b.tool('lookup_order',{'order_id':'O'}))
    def test_late_denied(self):
        c=self.case(); c['order']['age_days']=31; b=Sandbox(c)
        b.tool('lookup_order',{'order_id':'O'}); b.tool('check_policy',{})
        self.assertFalse(b.tool('issue_refund',{'order_id':'O','amount':25})['refunded'])
    def test_dry_never_spends(self):
        r=agent(self.case(),'baseline',True); self.assertEqual(r['estimated_usd'],0); self.assertTrue(r['objective_pass'])
if __name__=='__main__': unittest.main()
