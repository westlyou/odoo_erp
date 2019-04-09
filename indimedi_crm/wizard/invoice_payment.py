from odoo import models, fields, api


class InvoicePayment(models.TransientModel):
    _name = 'invoice.payment'
    
    invoice_ids = fields.Many2many('timesheet.invoice', string="Invoices")
    date_payment = fields.Date(string="Payment Date")
    amount = fields.Float(string="Payment Amount")
    remark = fields.Text(string="Note")
    
    @api.multi
    def action_mark_as_paid(self):
        payment = self.env['timesheet.invoice.payment']
        
        payment_id = payment.create({
                        'date_payment': self.date_payment,
                        'amount': self.amount,
                        'remark': self.remark
                            })
        self.invoice_ids.write({'is_paid': True, 'payment_id': payment_id.id})
        return {
                'name': "Invoice Payment",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': payment_id.id,
                'res_model': 'timesheet.invoice.payment',
                'target': 'self',
                
            }