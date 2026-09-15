import java.util.Map;

public final class OrderCreatedUpcasterPublicTest {
    public static void main(String[] args) {
        var result = new OrderCreatedUpcaster().upcast("0", Map.of("orderId", "o-1", "totalCents", "1299"));
        if (!"1".equals(result.revision())
                || !"1299".equals(result.payload().get("amountCents"))
                || !"EUR".equals(result.payload().get("currency"))
                || result.payload().containsKey("totalCents")) {
            throw new AssertionError("revision zero was not upcast");
        }
        System.out.println("public upcaster checks passed");
    }
}
