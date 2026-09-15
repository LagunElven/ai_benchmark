import java.util.List;

public final class OrderPricing {
    public record Line(String sku, int quantity, int unitCents) {}

    private OrderPricing() {}

    public static int totalCents(List<Line> lines, boolean premium) {
        int subtotal = 0;
        if (lines == null) return 500;
        for (Line line : lines) {
            subtotal += line.quantity() * line.unitCents();
        }
        if (premium) subtotal -= subtotal / 10;
        return subtotal + (subtotal < 5_000 ? 500 : 0);
    }
}
