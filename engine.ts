export enum CustomerTier {
    FREE = "free",
    PRO = "pro",
    ENTERPRISE = "enterprise"
}

export enum MessageRole {
    CUSTOMER = "customer",
    AGENT = "agent",
    SYSTEM = "system"
}

export enum TicketStatus {
    OPEN = "open",
    PENDING = "pending",
    RESOLVED = "resolved",
    CLOSED = "closed"
}

export enum ActionType {
    REPLY = "reply",
    LOOKUP_BILLING = "lookup_billing",
    TRIGGER_REFUND = "trigger_refund",
    UPDATE_SUBSCRIPTION = "update_subscription",
    CLOSE_TICKET = "close_ticket",
    UPDATE_CUSTOMER_RECORD = "update_customer_record",
    OFFER_RETENTION_CREDIT = "offer_retention_credit",
    OFFER_LOYALTY_DISCOUNT = "offer_loyalty_discount"
}

export interface ChatMessage {
    role: MessageRole;
    content: string;
}

export interface CustomerInfo {
    name: string;
    tier: CustomerTier;
}

export interface Observation {
    ticket_id: string;
    customer_info: CustomerInfo;
    last_message: string;
    chat_history: ChatMessage[];
    available_tools: string[];
    current_status: TicketStatus;
}

export interface Action {
    action_type: ActionType;
    payload: Record<string, any>;
}

export interface Reward {
    value: number;
    reason: string;
    is_terminal: boolean;
}

export class CompanyPolicy {
    static REFUND_WINDOW_DAYS = 30;
    static PRO_RATED_REFUND_ALLOWED = true;
    static MAX_RETENTION_CREDIT_MONTHS = 1;
    static LOYALTY_DISCOUNT_PERCENT = 20;
    static EMAIL_VERIFICATION_REQUIRED = true;

    static getPolicyText(): string {
        return `
        Company Policy:
        1. Refunds: Only allowed within 30 days of the invoice date.
        2. Pro-rated Refunds: Allowed for mid-cycle cancellations. Calculate as (remaining days / total days) * invoice amount.
        3. Retention: Offer 1 month credit for churn risk.
        4. Loyalty: For Enterprise customers or high-value churn, offer a 20% Loyalty Discount.
        5. Security: Email updates require a verification step.
        `;
    }
}

export class MockDatabase {
    customers: Record<string, any>;

    constructor() {
        const now = new Date();
        const fifteenDaysAgo = new Date(now.getTime() - 15 * 24 * 60 * 60 * 1000);
        const fiveDaysAgo = new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000);
        const fourHundredDaysAgo = new Date(now.getTime() - 400 * 24 * 60 * 60 * 1000);

        this.customers = {
            "cust_001": {
                "name": "Alice Smith",
                "email": "alice@example.com",
                "tier": CustomerTier.PRO,
                "subscription_date": fifteenDaysAgo.toISOString(),
                "billing_history": [
                    {
                        "id": "inv_101", 
                        "date": fifteenDaysAgo.toISOString().split('T')[0], 
                        "amount": 29.99, 
                        "status": "paid",
                        "period_start": fifteenDaysAgo.toISOString().split('T')[0],
                        "period_end": new Date(fifteenDaysAgo.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
                    }
                ],
                "usage_logs": ["Login: 2024-03-01", "Export Data: 2024-03-05"],
                "verified": true
            },
            "cust_002": {
                "name": "Enterprise Corp",
                "email": "admin@enterprise.com",
                "tier": CustomerTier.ENTERPRISE,
                "subscription_date": fourHundredDaysAgo.toISOString(),
                "billing_history": [
                    {
                        "id": "inv_501", 
                        "date": fiveDaysAgo.toISOString().split('T')[0], 
                        "amount": 499.99, 
                        "status": "paid",
                        "period_start": fiveDaysAgo.toISOString().split('T')[0],
                        "period_end": new Date(fiveDaysAgo.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
                    }
                ],
                "usage_logs": ["API Call: 10k/day", "User Added: 50"],
                "verified": true
            }
        };
    }

    updateEmail(customerId: string, newEmail: string): boolean {
        if (this.customers[customerId]) {
            this.customers[customerId].email = newEmail;
            return true;
        }
        return false;
    }

    issueRefund(customerId: string, invoiceId: string, amount: number): boolean {
        if (this.customers[customerId]) {
            const inv = this.customers[customerId].billing_history.find((i: any) => i.id === invoiceId);
            if (inv) {
                inv.status = "refunded";
                inv.refund_amount = amount;
                return true;
            }
        }
        return false;
    }
}

export class SaaSSupportEnv {
    db: MockDatabase;
    currentTicket: any;
    currentCustomerId: string | null;
    isTerminal: boolean;
    stepsTaken: number;
    actionHistory: Action[];
    taskDifficulty: string;
    verificationPending: boolean;

    constructor() {
        this.db = new MockDatabase();
        this.currentTicket = null;
        this.currentCustomerId = null;
        this.isTerminal = false;
        this.stepsTaken = 0;
        this.actionHistory = [];
        this.taskDifficulty = "easy";
        this.verificationPending = false;
    }

    reset(ticketId: string, customerId: string, initialMessage: string, difficulty: string = "easy"): Observation {
        this.currentCustomerId = customerId;
        this.taskDifficulty = difficulty;
        this.currentTicket = {
            id: ticketId,
            customer_id: customerId,
            last_message: initialMessage,
            history: [{ role: MessageRole.CUSTOMER, content: initialMessage }],
            status: TicketStatus.OPEN
        };
        this.isTerminal = false;
        this.stepsTaken = 0;
        this.actionHistory = [];
        this.verificationPending = false;
        return this.getObservation();
    }

    getObservation(): Observation {
        const customer = this.db.customers[this.currentCustomerId!];
        return {
            ticket_id: this.currentTicket.id,
            customer_info: { name: customer.name, tier: customer.tier },
            last_message: this.currentTicket.last_message,
            chat_history: this.currentTicket.history,
            available_tools: Object.values(ActionType),
            current_status: this.currentTicket.status
        };
    }

    step(action: Action): [Observation, Reward] {
        if (this.isTerminal) {
            throw new Error("Environment is terminal.");
        }

        this.stepsTaken++;
        this.actionHistory.push(action);
        let success = false;
        let infoMsg = "";
        let stepReward = -0.05;

        switch (action.action_type) {
            case ActionType.LOOKUP_BILLING:
                stepReward += 0.1;
                const billing = this.db.customers[this.currentCustomerId!].billing_history;
                infoMsg = `Billing Records: ${JSON.stringify(billing)}. ${CompanyPolicy.getPolicyText()}`;
                success = true;
                break;

            case ActionType.UPDATE_CUSTOMER_RECORD:
                const field = action.payload.field;
                const value = action.payload.value;
                if (field === "email") {
                    if (this.verificationPending) {
                        this.db.updateEmail(this.currentCustomerId!, value);
                        infoMsg = "Email updated successfully after verification.";
                        success = true;
                        this.verificationPending = false;
                    } else {
                        infoMsg = "Security: Please verify the identity first.";
                        this.verificationPending = true;
                        success = false;
                    }
                }
                break;

            case ActionType.TRIGGER_REFUND:
                const invId = action.payload.invoice_id;
                const amount = action.payload.amount || 0;
                const validIds = this.db.customers[this.currentCustomerId!].billing_history.map((i: any) => i.id);
                
                if (!validIds.includes(invId)) {
                    stepReward -= 0.5;
                    infoMsg = `Error: Invoice ${invId} not found.`;
                    success = false;
                } else {
                    const inv = this.db.customers[this.currentCustomerId!].billing_history.find((i: any) => i.id === invId);
                    const invDate = new Date(inv.date);
                    const diffDays = Math.floor((new Date().getTime() - invDate.getTime()) / (1000 * 60 * 60 * 24));
                    
                    if (diffDays <= CompanyPolicy.REFUND_WINDOW_DAYS) {
                        this.db.issueRefund(this.currentCustomerId!, invId, amount);
                        infoMsg = `Refund of ${amount} issued for ${invId}.`;
                        success = true;
                    } else {
                        infoMsg = "Refund rejected by Policy: Outside 30-day window.";
                        success = false;
                    }
                }
                break;

            case ActionType.OFFER_LOYALTY_DISCOUNT:
                if (this.db.customers[this.currentCustomerId!].tier === CustomerTier.ENTERPRISE) {
                    infoMsg = "Loyalty discount applied to Enterprise account.";
                    success = true;
                } else {
                    infoMsg = "Loyalty discount only available for Enterprise tier.";
                    success = false;
                }
                break;

            case ActionType.REPLY:
                const response = this.simulateCustomerResponse(action.payload.message || "");
                this.currentTicket.history.push({ role: MessageRole.AGENT, content: action.payload.message || "" });
                this.currentTicket.history.push({ role: MessageRole.CUSTOMER, content: response });
                this.currentTicket.last_message = response;
                success = true;
                break;

            case ActionType.CLOSE_TICKET:
                this.currentTicket.status = TicketStatus.RESOLVED;
                this.isTerminal = true;
                success = true;
                break;
        }

        if (infoMsg) {
            this.currentTicket.history.push({ role: MessageRole.SYSTEM, content: infoMsg });
        }

        let rewardVal = stepReward;
        if (this.isTerminal && success) {
            rewardVal += 1.0;
        }

        return [this.getObservation(), { value: rewardVal, reason: infoMsg || "Action processed.", is_terminal: this.isTerminal }];
    }

    simulateCustomerResponse(agentMsg: string): string {
        if (this.taskDifficulty === "easy") {
            return "Thank you, that sounds good. Please proceed.";
        } else if (this.taskDifficulty === "medium") {
            return "I see. Can you explain how you calculated that amount?";
        } else {
            const responses = [
                "This is unacceptable! I've been a loyal customer for years.",
                "I don't have time for this. Just fix it or I'm canceling.",
                "Why is this so complicated? I just want my money back."
            ];
            return responses[Math.floor(Math.random() * responses.length)];
        }
    }

    state(): any {
        return {
            db: this.db.customers,
            ticket: this.currentTicket,
            steps: this.stepsTaken,
            terminal: this.isTerminal
        };
    }
}
