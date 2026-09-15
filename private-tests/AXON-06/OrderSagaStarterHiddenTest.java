public final class OrderSagaStarterHiddenTest {
    public static void main(String[] args) {
        var starter = new OrderSagaStarter();
        starter.onOrderPlaced("o-1", "customer-1");
        starter.onPaymentRequested("o-1", "payment-1");
        starter.onPaymentRequested("o-2", "payment-2");
        if (starter.activeSagas() != 2 || !"o-1".equals(starter.orderFor("payment-1"))
                || !"o-2".equals(starter.orderFor("payment-2"))) {
            throw new AssertionError("multiple start paths created wrong saga associations");
        }
        starter.end("o-1");
        if (starter.orderFor("customer-1") != null || starter.orderFor("payment-1") != null
                || starter.activeSagas() != 1) {
            throw new AssertionError("completed saga retained an association");
        }
        starter.onOrderPlaced("", "bad");
        starter.onPaymentRequested("o-2", " ");
        if (starter.orderFor("bad") != null || starter.orderFor(" ") != null) {
            throw new AssertionError("blank association accepted");
        }
        System.out.println("hidden saga-start checks passed");
    }
}
