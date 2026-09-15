import java.util.LinkedHashMap;
import java.util.Map;

public final class OrderCreatedUpcasterHiddenTest {
    public static void main(String[] args) {
        var source = new LinkedHashMap<String, String>();
        source.put("orderId", "o-2");
        source.put("totalCents", "500");
        var result = new OrderCreatedUpcaster().upcast("0", source);
        if (source.containsKey("amountCents") || !"500".equals(result.payload().get("amountCents"))) {
            throw new AssertionError("source map was mutated");
        }
        var current = new LinkedHashMap<String, String>();
        current.put("orderId", "o-3");
        current.put("amountCents", "700");
        current.put("currency", "CHF");
        current.put("newField", "kept");
        var pass = new OrderCreatedUpcaster().upcast("1", current);
        if (!"1".equals(pass.revision()) || !"kept".equals(pass.payload().get("newField"))) {
            throw new AssertionError("current revision changed");
        }
        try {
            new OrderCreatedUpcaster().upcast("9", Map.of());
            throw new AssertionError("unsupported revision accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        System.out.println("hidden upcaster checks passed");
    }
}
