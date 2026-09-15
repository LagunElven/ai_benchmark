import java.math.BigDecimal;
import java.math.RoundingMode;

public final class BenefitRule {
    private BenefitRule() {}

    public static BigDecimal rebate(int tenureMonths, BigDecimal baseAmount) {
        BigDecimal rate = tenureMonths >= 12 ? new BigDecimal("0.05") : BigDecimal.ZERO;
        return baseAmount.add(baseAmount.multiply(rate));
    }
}
