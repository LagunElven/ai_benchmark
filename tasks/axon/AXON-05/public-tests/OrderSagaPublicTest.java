public final class OrderSagaPublicTest {
    public static void main(String[] args) {
        var saga = new OrderSaga();
        saga.start("o-1", "payment-1");
        if (!"o-1".equals(saga.orderFor("payment-1"))) {
            throw new AssertionError("saga association missing");
        }
        System.out.println("public saga checks passed");
    }
}
