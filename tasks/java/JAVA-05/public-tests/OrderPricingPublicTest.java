import java.util.List;

public final class OrderPricingPublicTest {
    public static void main(String[] args) {
        var lines = List.of(new OrderPricing.Line("A", 2, 3_000));
        if (OrderPricing.totalCents(lines, false) != 6_000) {
            throw new AssertionError("ordinary pricing changed");
        }
        System.out.println("public pricing checks passed");
    }
}
