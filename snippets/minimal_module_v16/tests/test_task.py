from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestTask(TransactionCase):

    def setUp(self):
        super().setUp()
        self.today = fields.Date.today()
        self.late = self.env["task.item"].create({"name": "late", "deadline": self.today - timedelta(days=2)})
        self.ok = self.env["task.item"].create({"name": "ok", "deadline": self.today + timedelta(days=2)})

    def test_is_late_compute_and_search(self):
        self.assertTrue(self.late.is_late)
        self.assertFalse(self.ok.is_late)
        found = self.env["task.item"].search([("is_late", "=", True), ("id", "in", (self.late | self.ok).ids)])
        self.assertEqual(found, self.late)
        not_late = self.env["task.item"].search([("is_late", "=", False), ("id", "in", (self.late | self.ok).ids)])
        self.assertEqual(not_late, self.ok)

    def test_workflow(self):
        with self.assertRaises(UserError):
            self.ok.action_done()  # not started yet
        self.ok.action_start()
        self.ok.action_done()
        self.assertEqual(self.ok.state, "done")
        self.assertFalse(self.ok.is_late)

    def test_negative_amount(self):
        with self.assertRaises(ValidationError):
            self.ok.amount = -1
