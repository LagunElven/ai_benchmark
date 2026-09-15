import java.util.HashMap;
import java.util.Map;

public final class OrderSaga {
    private final Map<String, String> associations = new HashMap<>();

    public void start(String orderId, String associationKey) {}

    public void associate(String orderId, String associationKey) {}

    public String orderFor(String associationKey) { return null; }

    public void end(String orderId) {}
}
