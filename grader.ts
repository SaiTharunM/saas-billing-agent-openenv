import { SaaSSupportEnv, ActionType, TicketStatus } from './engine';

export class Grader {
    static grade_task_1(env: SaaSSupportEnv): number {
        const verified = env.verificationPending || env.currentTicket.history.some((msg: any) => msg.role === 'system' && msg.content.includes("Security: Please verify"));
        const updated = env.db.customers["cust_001"].email === "alice_new@example.com";
        const resolved = env.currentTicket.status === TicketStatus.RESOLVED;

        if (updated && resolved) return 1.0;
        if (verified) return 0.5;
        return 0.0;
    }

    static grade_task_2(env: SaaSSupportEnv): number {
        const history = env.actionHistory;
        const lookedUp = history.some(a => a.action_type === ActionType.LOOKUP_BILLING);
        
        let correctRefund = false;
        let anyRefund = false;
        for (const action of history) {
            if (action.action_type === ActionType.TRIGGER_REFUND) {
                anyRefund = true;
                const payload = action.payload;
                if (payload.invoice_id === "inv_101" && Math.abs(parseFloat(payload.amount || "0") - 14.99) < 0.01) {
                    correctRefund = true;
                }
            }
        }
        
        if (correctRefund) return 1.0;
        if (anyRefund) return 0.5;
        if (lookedUp) return 0.2;
        return 0.0;
    }

    static grade_task_3(env: SaaSSupportEnv): number {
        const history = env.actionHistory;
        const loyaltyOffered = history.some(a => a.action_type === ActionType.OFFER_LOYALTY_DISCOUNT);
        const refundIssued = history.some(a => a.action_type === ActionType.TRIGGER_REFUND);

        if (loyaltyOffered && !refundIssued) return 1.0;
        if (loyaltyOffered && refundIssued) return 0.5;
        return 0.0;
    }
}
