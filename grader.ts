import { SaaSSupportEnv, ActionType, TicketStatus } from './engine';

export class Grader {

    // ✅ GLOBAL NORMALIZER (CRITICAL FIX)
    static normalizeScore(score: any): number {
        let s = Number(score);

        // Handle NaN / null / undefined
        if (isNaN(s) || s === null || s === undefined) {
            return 0.5;
        }

        // STRICT range (never 0 or 1)
        if (s <= 0) return 0.01;
        if (s >= 1) return 0.99;

        return s;
    }

    static grade_task_1(env: SaaSSupportEnv): number {
        const verified =
            env.verificationPending ||
            env.currentTicket.history.some(
                (msg: any) =>
                    msg.role === 'system' &&
                    msg.content.includes("Security: Please verify")
            );

        const updated =
            env.db.customers["cust_001"].email === "alice_new@example.com";

        const resolved =
            env.currentTicket.status === TicketStatus.RESOLVED;

        let score;

        if (updated && resolved) score = 1.0;
        else if (verified) score = 0.5;
        else score = 0.0;

        return Grader.normalizeScore(score); // ✅ FIX
    }

    static grade_task_2(env: SaaSSupportEnv): number {
        const history = env.actionHistory;

        const lookedUp = history.some(
            (a: any) => a.action_type === ActionType.LOOKUP_BILLING
        );

        let correctRefund = false;
        let anyRefund = false;

        for (const action of history) {
            if (action.action_type === ActionType.TRIGGER_REFUND) {
                anyRefund = true;

                const payload = action.payload || {};

                let amount = 0;
                try {
                    amount = parseFloat(payload.amount || "0");
                } catch {
                    amount = 0;
                }

                if (
                    payload.invoice_id === "inv_101" &&
                    Math.abs(amount - 14.99) < 0.01
                ) {
                    correctRefund = true;
                }
            }
        }

        let score;

        if (correctRefund) score = 1.0;
        else if (anyRefund) score = 0.5;
        else if (lookedUp) score = 0.2;
        else score = 0.0;

        return Grader.normalizeScore(score); // ✅ FIX
    }

    static grade_task_3(env: SaaSSupportEnv): number {
        const history = env.actionHistory;

        const loyaltyOffered = history.some(
            (a: any) =>
                a.action_type === ActionType.OFFER_LOYALTY_DISCOUNT
        );

        const refundIssued = history.some(
            (a: any) =>
                a.action_type === ActionType.TRIGGER_REFUND
        );

        let score;

        if (loyaltyOffered && !refundIssued) score = 1.0;
        else if (loyaltyOffered && refundIssued) score = 0.5;
        else score = 0.0;

        return Grader.normalizeScore(score); // ✅ FIX
    }
}