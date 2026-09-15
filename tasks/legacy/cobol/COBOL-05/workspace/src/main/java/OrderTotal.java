import java.math.BigDecimal;
import java.math.RoundingMode;

public final class OrderTotal {
    private static final BigDecimal MAX = new BigDecimal("9999999.99");

    private OrderTotal() {}

    public static BigDecimal calculate(BigDecimal subtotal, BigDecimal tax) {
        return subtotal.subtract(tax);
    }
}
