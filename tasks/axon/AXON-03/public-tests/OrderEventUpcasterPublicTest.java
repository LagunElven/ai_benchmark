import java.util.LinkedHashMap;

public final class OrderEventUpcasterPublicTest {
    public static void main(String[] args) {
        var payload = new LinkedHashMap<String, String>();
        payload.put("orderId", "o-1");
        payload.put("totalCents", "1250");
        var event = new OrderEventUpcaster().upcast("0", payload);
        if (!"2".equals(event.revision())
                || !"1250".equals(event.payload().get("amountCents"))
                || !"EUR".equals(event.payload().get("currency"))) {
            throw new AssertionError("revision chain was not applied");
        }
        System.out.println("public upcaster checks passed");
    }
}
