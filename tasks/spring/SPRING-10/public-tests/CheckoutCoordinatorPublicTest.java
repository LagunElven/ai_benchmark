import java.util.ArrayList;
import java.util.List;

public final class CheckoutCoordinatorPublicTest {
    public static void main(String[] args) {
        var events = new ArrayList<String>();
        var orders = new CheckoutCoordinator.OrderService() {
            public CheckoutCoordinator.Order find(String id) {
                return new CheckoutCoordinator.Order(id, 1250, CheckoutCoordinator.Status.PENDING);
            }

            public void updateStatus(String id, CheckoutCoordinator.Status status) {
                events.add("status:" + status);
            }
        };
        var payments = new CheckoutCoordinator.PaymentService() {
            public void charge(String id, int cents) { events.add("charge:" + cents); }

            public void refund(String id, int cents) { events.add("refund:" + cents); }
        };

        var outcome = new CheckoutCoordinator().complete("order-1", orders, payments);
        if (!outcome.completed() || outcome.status() != CheckoutCoordinator.Status.PAID) {
            throw new AssertionError("successful checkout was not reported");
        }
        if (!List.of("charge:1250", "status:PAID").equals(events)) {
            throw new AssertionError("payment and order update were not ordered");
        }
        System.out.println("public checkout checks passed");
    }
}
