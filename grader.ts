import { SaaSSupportEnv, ActionType, TicketStatus } from './engine';

export class Grader {
    static normalizeScore(score: any): number {
        const s = Number(score);

        if (isNaN(s) || s === null || s === undefined) {
            return 0.5;
        }

        if (s <= 0) return 0.01;
        if (s >= 1) return 0.99;
        return s;
    }

    static grade_task_1(env: SaaSSupportEnv): number {
        const currentTicket = env.currentTicket || { history: [], status: null };
        const history = currentTicket.history || [];

        const verified =
            env.verificationPending ||
            history.some(
                (msg: any) =>
                    msg.role === 'system' &&
                    msg.content.includes("Security: Please verify")
            );

        const updated =
            env.db.customers["cust_001"].email === "alice_new@example.com";

        const resolved =
            currentTicket.status === TicketStatus.RESOLVED;

        if (updated && resolved) return Grader.normalizeScore(0.99);
        if (verified) return Grader.normalizeScore(0.5);
        return Grader.normalizeScore(0.01);
    }

    static grade_task_2(env: SaaSSupportEnv): number {
        const history = env.actionHistory || [];

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

        if (correctRefund) return Grader.normalizeScore(0.99);
        if (anyRefund) return Grader.normalizeScore(0.5);
        if (lookedUp) return Grader.normalizeScore(0.2);
        return Grader.normalizeScore(0.01);
    }

    static grade_task_3(env: SaaSSupportEnv): number {
        const history = env.actionHistory || [];

        const loyaltyOffered = history.some(
            (a: any) => a.action_type === ActionType.OFFER_LOYALTY_DISCOUNT
        );

        const refundIssued = history.some(
            (a: any) => a.action_type === ActionType.TRIGGER_REFUND
        );

        if (loyaltyOffered && !refundIssued) return Grader.normalizeScore(0.99);
        if (loyaltyOffered && refundIssued) return Grader.normalizeScore(0.5);
        return Grader.normalizeScore(0.01);
    }

    static grade(taskId: string, env: SaaSSupportEnv): number {
        if (taskId === "task_1") return Grader.normalizeScore(Grader.grade_task_1(env));
        if (taskId === "task_2") return Grader.normalizeScore(Grader.grade_task_2(env));
        if (taskId === "task_3") return Grader.normalizeScore(Grader.grade_task_3(env));
        return Grader.normalizeScore(0.01);
    }
}
