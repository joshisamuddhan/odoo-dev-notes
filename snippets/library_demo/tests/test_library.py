from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestLibrary(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.book = cls.env["library.book"].create({"name": "Dune", "isbn": "ISBN-1", "price": 10})
        cls.partner = cls.env["res.partner"].create({"name": "Reader", "email": "r@example.com"})
        today = fields.Date.today()
        cls.loan = cls.env["library.loan"].create({
            "book_id": cls.book.id, "partner_id": cls.partner.id,
            "date_out": today, "date_due": today + timedelta(days=7),
        })

    def test_confirm_and_return(self):
        self.loan.action_confirm()
        self.assertEqual(self.book.state, "borrowed")
        self.assertEqual(self.loan.state, "open")
        self.loan.action_return()
        self.assertEqual(self.book.state, "available")

    def test_cannot_confirm_unavailable_book(self):
        self.book.state = "lost"
        with self.assertRaises(UserError):
            self.loan.action_confirm()

    def test_date_constraint(self):
        with self.assertRaises(ValidationError):
            self.loan.date_due = self.loan.date_out - timedelta(days=1)

    def test_overdue_cron_and_fine(self):
        self.loan.action_confirm()
        today = fields.Date.today()
        # write both dates together so the date constraint stays satisfied
        self.loan.write({"date_out": today - timedelta(days=10), "date_due": today - timedelta(days=3)})
        self.env["library.loan"]._cron_mark_overdue()
        self.assertEqual(self.loan.state, "overdue")
        self.assertEqual(self.loan.days_overdue, 3)
        self.assertEqual(self.loan.fine, 15.0)

    def test_isbn_unique(self):
        with self.assertRaises(Exception), self.cr.savepoint():
            self.env["library.book"].create({"name": "Dup", "isbn": "ISBN-1"})
