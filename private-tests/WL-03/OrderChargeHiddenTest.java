import java.math.BigDecimal;

public final class OrderChargeHiddenTest {
    public static void main(String[] args) {
        if (!new BigDecimal("52.50").equals(
                OrderCharge.totalWithShipping(new BigDecimal("40.00"), " express "))) {
            throw new AssertionError("express mode normalization or fee is wrong");
        }
        BigDecimal pickup = OrderCharge.totalWithShipping(new BigDecimal("50.005"), "PICKUP");
        if (!new BigDecimal("50.01").equals(pickup) || pickup.scale() != 2) {
            throw new AssertionError("pickup decimal rounding is wrong: " + pickup);
        }
        assertInvalid(new BigDecimal("-0.01"), "STANDARD");
        assertInvalid(new BigDecimal("10.00"), "UNKNOWN");
        assertInvalid(new BigDecimal("10.00"), null);
        System.out.println("hidden WLanguage order-charge checks passed");
    }

    private static void assertInvalid(BigDecimal subtotal, String mode) {
        try {
            OrderCharge.totalWithShipping(subtotal, mode);
            throw new AssertionError("invalid order charge input was accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
    }
}
