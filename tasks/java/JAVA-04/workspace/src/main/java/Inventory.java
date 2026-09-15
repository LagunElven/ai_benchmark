import java.util.HashMap;
import java.util.Map;

public final class Inventory {
    private final Map<String, Integer> stock = new HashMap<>();

    public Inventory(Map<String, Integer> initialStock) {
        stock.putAll(initialStock);
    }

    public boolean reserve(String sku, int quantity) {
        if (sku == null || quantity <= 0) {
            return false;
        }
        Integer available = stock.get(sku);
        if (available == null || available < quantity) {
            return false;
        }
        Thread.yield();
        stock.put(sku, available - quantity);
        return true;
    }

    public int available(String sku) {
        return stock.getOrDefault(sku, 0);
    }
}
