import java.util.Arrays;

public final class OrderPricingHiddenTest {
    public static void main(String[] args) {
        var lines = Arrays.asList(
                new OrderPricing.Line("A", 1, 10_001));
        if (OrderPricing.totalCents(lines, true) != 9_001) {
            throw new AssertionError("premium discount is wrong");
        }
        if (OrderPricing.totalCents(java.util.List.of(new OrderPricing.Line("ship", 1, 4_500)), false) != 5_000) {
            throw new AssertionError("shipping threshold is wrong");
        }
        if (OrderPricing.totalCents(null, false) != 0
                || OrderPricing.totalCents(java.util.List.of(), false) != 0) {
            throw new AssertionError("empty order should have no charges");
        }
        for (var invalid : new OrderPricing.Line[] {
                null, new OrderPricing.Line("bad", 0, 10), new OrderPricing.Line("bad", 1, -1)}) {
            try {
                OrderPricing.totalCents(java.util.List.of(invalid), false);
                throw new AssertionError("invalid line accepted");
            } catch (IllegalArgumentException expected) {
                // expected
            }
        }
        try {
            OrderPricing.totalCents(java.util.List.of(new OrderPricing.Line("huge", Integer.MAX_VALUE, Integer.MAX_VALUE)), false);
            throw new AssertionError("integer overflow accepted");
        } catch (ArithmeticException expected) {
            // expected
        }
        System.out.println("hidden pricing checks passed");
    }
}
