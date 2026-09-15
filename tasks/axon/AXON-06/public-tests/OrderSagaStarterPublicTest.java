public final class OrderSagaStarterPublicTest {
    public static void main(String[] args) {
        var starter = new OrderSagaStarter();
        starter.onOrderPlaced("o-1", "customer-1");
        if (starter.activeSagas() != 1 || !"o-1".equals(starter.orderFor("customer-1"))) {
            throw new AssertionError("order start path failed");
        }
        System.out.println("public saga-start checks passed");
    }
}
