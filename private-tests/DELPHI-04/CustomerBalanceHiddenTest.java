import java.math.BigDecimal;

public final class CustomerBalanceHiddenTest {
    public static void main(String[] args) {
        if (!new BigDecimal("0.00").equals(
                CustomerBalance.calculate(new BigDecimal("10.00"), new BigDecimal("10.01")))) {
            throw new AssertionError("negative balance was not clamped");
        }
        BigDecimal actual = CustomerBalance.calculate(new BigDecimal("0.10"), new BigDecimal("0.20"));
        if (!new BigDecimal("0.00").equals(actual) || actual.scale() != 2) {
            throw new AssertionError("Currency scale/clamp mismatch: " + actual);
        }
        System.out.println("hidden Delphi migration checks passed");
    }
}
