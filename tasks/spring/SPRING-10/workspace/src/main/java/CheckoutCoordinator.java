public final class CheckoutCoordinator {
    public enum Status { PENDING, PAID, PAYMENT_FAILED }

    public record Order(String id, int cents, Status status) {}

    public record Outcome(boolean completed, Status status) {}

    public interface OrderService {
        Order find(String orderId);

        void updateStatus(String orderId, Status status);
    }

    public interface PaymentService {
        void charge(String orderId, int cents);

        void refund(String orderId, int cents);
    }

    public Outcome complete(
            String orderId, OrderService orders, PaymentService payments) {
        Order order = orders.find(orderId);
        orders.updateStatus(order.id(), Status.PAID);
        payments.charge(order.id(), order.cents());
        return new Outcome(true, Status.PAID);
    }
}
