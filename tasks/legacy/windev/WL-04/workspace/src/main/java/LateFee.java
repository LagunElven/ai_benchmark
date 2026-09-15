import java.math.BigDecimal;
import java.math.RoundingMode;

public final class LateFee {
    private LateFee() {}

    public static BigDecimal calculate(BigDecimal amount, int daysLate) {
        BigDecimal rate = daysLate > 30 ? new BigDecimal("0.10") : new BigDecimal("0.05");
        return amount.multiply(rate);
    }
}
