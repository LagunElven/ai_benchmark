import java.util.HashMap;
import java.util.Map;

public final class OrderSagaStarter {
    private final Map<String, String> associations = new HashMap<>();

    public void onOrderPlaced(String orderId, String customerKey) {}

    public void onPaymentRequested(String orderId, String paymentKey) {}

    public int activeSagas() { return 0; }

    public String orderFor(String key) { return null; }

    public void end(String orderId) {}
}
