import java.util.ArrayList;
import java.util.List;

public final class CheckoutCoordinatorHiddenTest {
    public static void main(String[] args) {
        paymentFailureMarksOrderAndPropagates();
        paidOrdersAreIdempotent();
        updateFailureCompensatesAndPreservesCause();
        System.out.println("hidden checkout checks passed");
    }

    private static void paymentFailureMarksOrderAndPropagates() {
        var statuses = new ArrayList<CheckoutCoordinator.Status>();
        var orders = orders(CheckoutCoordinator.Status.PENDING, statuses, false);
        var refunds = new int[1];
        var payments = new CheckoutCoordinator.PaymentService() {
            public void charge(String id, int cents) { throw new IllegalStateException("declined"); }

            public void refund(String id, int cents) { refunds[0]++; }
        };
        try {
            new CheckoutCoordinator().complete("o-1", orders, payments);
            throw new AssertionError("payment failure was swallowed");
        } catch (IllegalStateException expected) {
            if (!"declined".equals(expected.getMessage())) throw new AssertionError("wrong cause");
        }
        if (!List.of(CheckoutCoordinator.Status.PAYMENT_FAILED).equals(statuses)) {
            throw new AssertionError("payment failure was not persisted");
        }
        if (refunds[0] != 0) throw new AssertionError("declined payment was refunded");
    }

    private static void paidOrdersAreIdempotent() {
        var statuses = new ArrayList<CheckoutCoordinator.Status>();
        var orders = orders(CheckoutCoordinator.Status.PAID, statuses, false);
        var charges = new int[1];
        var payments = new CheckoutCoordinator.PaymentService() {
            public void charge(String id, int cents) { charges[0]++; }

            public void refund(String id, int cents) {}
        };
        var outcome = new CheckoutCoordinator().complete("o-1", orders, payments);
        if (!outcome.completed() || outcome.status() != CheckoutCoordinator.Status.PAID
                || charges[0] != 0 || !statuses.isEmpty()) {
            throw new AssertionError("paid order was not idempotent");
        }
    }

    private static void updateFailureCompensatesAndPreservesCause() {
        var events = new ArrayList<String>();
        var orders = new CheckoutCoordinator.OrderService() {
            public CheckoutCoordinator.Order find(String id) {
                return new CheckoutCoordinator.Order(id, 990, CheckoutCoordinator.Status.PENDING);
            }

            public void updateStatus(String id, CheckoutCoordinator.Status status) {
                events.add("status:" + status);
                throw new IllegalStateException("order store down");
            }
        };
        var payments = new CheckoutCoordinator.PaymentService() {
            public void charge(String id, int cents) { events.add("charge"); }

            public void refund(String id, int cents) { events.add("refund:" + cents); }
        };
        try {
            new CheckoutCoordinator().complete("o-1", orders, payments);
            throw new AssertionError("order update failure was swallowed");
        } catch (IllegalStateException expected) {
            if (!"order store down".equals(expected.getMessage())) throw new AssertionError("wrong failure");
        }
        if (!List.of("charge", "status:PAID", "refund:990").equals(events)) {
            throw new AssertionError("successful charge was not compensated");
        }
    }

    private static CheckoutCoordinator.OrderService orders(
            CheckoutCoordinator.Status status, List<CheckoutCoordinator.Status> statuses,
            boolean fail) {
        return new CheckoutCoordinator.OrderService() {
            public CheckoutCoordinator.Order find(String id) {
                return new CheckoutCoordinator.Order(id, 500, status);
            }

            public void updateStatus(String id, CheckoutCoordinator.Status next) {
                statuses.add(next);
                if (fail) throw new IllegalStateException("status failure");
            }
        };
    }
}
