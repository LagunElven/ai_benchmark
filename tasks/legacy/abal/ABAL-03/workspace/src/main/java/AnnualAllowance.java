import java.math.BigDecimal;
import java.math.RoundingMode;

public final class AnnualAllowance {
    private AnnualAllowance() {}

    public static BigDecimal payable(
            BigDecimal claimAmount, BigDecimal remainingCap, boolean approved) {
        if (claimAmount == null || remainingCap == null
                || claimAmount.signum() < 0 || remainingCap.signum() < 0) {
            throw new IllegalArgumentException("invalid allowance amount");
        }
        if (!approved) return claimAmount.setScale(2, RoundingMode.HALF_UP);
        return claimAmount.max(remainingCap).setScale(2, RoundingMode.HALF_UP);
    }
}
