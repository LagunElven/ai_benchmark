import java.util.HashMap;
import java.util.Map;

public final class StockProjection {
    public record StockAdded(String sku, int quantity) {}
    public record StockRemoved(String sku, int quantity) {}
    private final Map<String, Integer> quantities = new HashMap<>();

    public void handle(Object event) {
        if (event instanceof StockAdded added) {
            quantities.merge(added.sku(), added.quantity(), Integer::sum);
        }
    }

    public int available(String sku) { return quantities.getOrDefault(sku, 0); }
}
