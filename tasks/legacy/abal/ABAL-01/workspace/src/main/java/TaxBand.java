import java.math.BigDecimal;

public final class TaxBand {
    public enum Code { BASIC, STANDARD, HIGH, NON_RESIDENT }

    private TaxBand() {}

    public static Code classify(BigDecimal annualIncome, boolean resident) {
        if (annualIncome == null || annualIncome.signum() < 0) {
            throw new IllegalArgumentException("invalid annual income");
        }
        if (!resident) return Code.NON_RESIDENT;
        if (annualIncome.compareTo(new BigDecimal("1000000")) < 0) return Code.BASIC;
        if (annualIncome.compareTo(new BigDecimal("3000000")) <= 0) return Code.STANDARD;
        return Code.HIGH;
    }
}
