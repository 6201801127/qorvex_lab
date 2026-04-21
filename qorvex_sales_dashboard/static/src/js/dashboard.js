/** @odoo-module **/

import { Component, onWillStart, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class SalesDashboard extends Component {

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            orders: [],
            date_from: null,
            date_to: null,
        });

        // Store previous IDs to detect new records
        this.previousIds = new Set();

        // Load initial data
        onWillStart(async () => {
            await this.loadData();
            this.previousIds = new Set(this.state.orders.map(o => o.id));
        });

        // Start polling
        onMounted(() => {
            this.polling = setInterval(async () => {
                try {
                    const oldIds = new Set(this.previousIds);

                    await this.loadData();

                    const newOrders = this.state.orders.filter(
                        o => !oldIds.has(o.id)
                    );

                    // Show notification if new order found
                    if (newOrders.length > 0) {
                        this.notification.add(
                            `New Order Created: ${newOrders[0].name}`,
                            { type: "success" }
                        );
                    }

                    // Update stored IDs
                    this.previousIds = new Set(this.state.orders.map(o => o.id));

                } catch (error) {
                    console.error("Polling error:", error);
                }
            }, 3000);
        });

        // Cleanup
        onWillUnmount(() => {
            clearInterval(this.polling);
        });
    }

    async loadData() {
        const data = await this.orm.call(
            "sale.dashboard",
            "get_sales_data",
            [this.state.date_from, this.state.date_to]
        );
        this.state.orders = data;
    }

    async onFilterApply() {
        await this.loadData();
        this.previousIds = new Set(this.state.orders.map(o => o.id));
    }
}

SalesDashboard.template = "sale_dashboard_template";
registry.category("actions").add("sales_dashboard_action", SalesDashboard);