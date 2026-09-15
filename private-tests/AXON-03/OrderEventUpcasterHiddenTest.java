import java.util.LinkedHashMap;
import java.util.Map;

public final class OrderEventUpcasterHiddenTest {
    public static void main(String[] args) {
        var old = new LinkedHashMap<String, String>();
        old.put("orderId", "o-2");
        old.put("totalCents", "500");
        old.put("custom", "keep");
        var result = new OrderEventUpcaster().upcast("0", old);
        if (old.containsKey("amountCents") || !"keep".equals(result.payload().get("custom"))) {
            throw new AssertionError("input mutation or unknown field loss");
        }
        try {
            result.payload().put("forbidden", "mutation");
            throw new AssertionError("upcast result is mutable");
        } catch (UnsupportedOperationException expected) {
            // expected
        }
        var existing = new LinkedHashMap<String, String>();
        existing.put("amountCents", "700");
        existing.put("currency", "CHF");
        var current = new OrderEventUpcaster().upcast("1", existing);
        if (!"2".equals(current.revision()) || !"CHF".equals(current.payload().get("currency"))) {
            throw new AssertionError("existing currency was overwritten");
        }
        var pass = new OrderEventUpcaster().upcast("2", Map.of("currency", "GBP"));
        if (!"GBP".equals(pass.payload().get("currency"))) {
            throw new AssertionError("current event was not preserved");
        }
        try {
            new OrderEventUpcaster().upcast("9", Map.of());
            throw new AssertionError("unknown revision accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        System.out.println("hidden upcaster checks passed");
    }
}
