import java.math.BigDecimal;

public final class LateFeeHiddenTest {
    public static void main(String[] args) {
        if (!new BigDecimal("0.00").equals(LateFee.calculate(new BigDecimal("100.00"), -1))) {
            throw new AssertionError("non-positive days must be free");
        }
        if (!new BigDecimal("10.00").equals(LateFee.calculate(new BigDecimal("100.00"), 31))) {
            throw new AssertionError("long delay rate mismatch");
        }
        BigDecimal actual = LateFee.calculate(new BigDecimal("0.10"), 1);
        if (!new BigDecimal("0.01").equals(actual) || actual.scale() != 2) {
            throw new AssertionError("late fee decimal scale mismatch: " + actual);
        }
        System.out.println("hidden WLanguage migration checks passed");
    }
}
