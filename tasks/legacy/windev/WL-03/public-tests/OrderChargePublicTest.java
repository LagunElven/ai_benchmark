import java.math.BigDecimal;

public final class OrderChargePublicTest {
    public static void main(String[] args) {
        if (!new BigDecimal("46.90").equals(
                OrderCharge.totalWithShipping(new BigDecimal("40.00"), "STANDARD"))) {
            throw new AssertionError("standard shipping below threshold is wrong");
        }
        if (!new BigDecimal("50.00").equals(
                OrderCharge.totalWithShipping(new BigDecimal("50.00"), "STANDARD"))) {
            throw new AssertionError("free-shipping threshold is inclusive");
        }
        System.out.println("public WLanguage order-charge checks passed");
    }
}
