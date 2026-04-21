from odoo import models, api
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override the create method to emit real-time notifications when new sales orders are created.
        This method extends the default Odoo behavior by sending a message through the bus service for each newly created sales order. 
        The frontend dashboard listens to this channel and updates automatically when a new order is added.

        Parameters:
            vals_list (list[dict]): A list of dictionaries containing
                values for creating one or multiple sales orders.

        Returns:
            recordset: The created sale.order records.

        Behavior:
            - Calls the parent create() to generate records.
            - Iterates over each created record.
            - Logs a message for debugging/tracking purposes.
            - Sends a notification via bus.bus on the
              'sale_dashboard_channel'.

        Notification Payload Structure:
            {
                'type': 'new_order',
                'data': {
                    'id': int,
                    'name': str,
                    'customer': str,
                    'total': float,
                    'date': str (ISO format)
                }
            }

        Notes:
            - Uses Odoo bus service for real-time communication.
            - Channel format includes database name to ensure proper
              routing in multi-database environments.
            - Intended to support live dashboard updates without
              requiring manual refresh.
        """
        records = super().create(vals_list)

        for record in records:
            _logger.warning("BUS SENT: %s", record.name)
            self.env['bus.bus']._sendone(
                (self._cr.dbname, 'sale_dashboard_channel', 0),
                'notification',
                {
                    'type': 'new_order',
                    'data': {
                        'id': record.id,
                        'name': record.name,
                        'customer': record.partner_id.name,
                        'total': record.amount_total,
                        'date': record.date_order.isoformat() if record.date_order else False,
                    }
                }
            )
        return records
