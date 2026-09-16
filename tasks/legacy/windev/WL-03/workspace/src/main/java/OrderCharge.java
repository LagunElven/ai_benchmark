import java.math.BigDecimal;
import java.math.RoundingMode;

public final class OrderCharge {
    private OrderCharge() {}

    public static BigDecimal totalWithShipping(BigDecimal subtotal, String mode) {
        if (subtotal == null || subtotal.signum() < 0) {
            throw new IllegalArgumentException("invalid subtotal");
        }
        BigDecimal shipping;
        if ("PICKUP".equalsIgnoreCase(mode)) {
            shipping = BigDecimal.ZERO;
        } else if ("EXPRESS".equalsIgnoreCase(mode)) {
            shipping = new BigDecimal("12.50");
        } else if ("STANDARD".equalsIgnoreCase(mode)) {
            shipping = subtotal.compareTo(new BigDecimal("50.00")) > 0
                    ? BigDecimal.ZERO : new BigDecimal("6.90");
        } else {
            throw new IllegalArgumentException("unknown delivery mode");
        }
        return subtotal.add(shipping);
    }
}
