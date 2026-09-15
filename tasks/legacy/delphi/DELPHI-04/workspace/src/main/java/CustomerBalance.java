import java.math.BigDecimal;
import java.math.RoundingMode;

public final class CustomerBalance {
    private CustomerBalance() {}

    public static BigDecimal calculate(BigDecimal grossAmount, BigDecimal credit) {
        return grossAmount.add(credit);
    }
}
