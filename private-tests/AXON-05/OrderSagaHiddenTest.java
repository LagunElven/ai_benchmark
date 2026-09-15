public final class OrderSagaHiddenTest {
    public static void main(String[] args) {
        var saga = new OrderSaga();
        saga.start("o-1", "payment-1");
        saga.associate("o-1", "customer-1");
        saga.start("o-2", "payment-2");
        if (!"o-1".equals(saga.orderFor("customer-1"))
                || !"o-2".equals(saga.orderFor("payment-2"))) {
            throw new AssertionError("multiple saga associations resolved incorrectly");
        }
        saga.end("o-1");
        if (saga.orderFor("payment-1") != null || saga.orderFor("customer-1") != null
                || !"o-2".equals(saga.orderFor("payment-2"))) {
            throw new AssertionError("ending one saga removed or retained wrong keys");
        }
        saga.start("", "bad");
        saga.associate("o-2", " ");
        if (saga.orderFor("bad") != null || saga.orderFor(" ") != null) {
            throw new AssertionError("blank association accepted");
        }
        System.out.println("hidden saga checks passed");
    }
}
