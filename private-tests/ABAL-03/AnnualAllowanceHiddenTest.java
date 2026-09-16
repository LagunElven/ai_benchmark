import java.math.BigDecimal;

public final class AnnualAllowanceHiddenTest {
    public static void main(String[] args) {
        if (!new BigDecimal("100.00").equals(AnnualAllowance.payable(
                new BigDecimal("120.00"), new BigDecimal("100.00"), true))) {
            throw new AssertionError("approved claim was not capped");
        }
        BigDecimal actual = AnnualAllowance.payable(
                new BigDecimal("0.105"), new BigDecimal("1.00"), true);
        if (!new BigDecimal("0.11").equals(actual) || actual.scale() != 2) {
            throw new AssertionError("allowance rounding is wrong: " + actual);
        }
        assertInvalid(null, BigDecimal.ONE, true);
        assertInvalid(BigDecimal.ONE, null, true);
        assertInvalid(new BigDecimal("-0.01"), BigDecimal.ONE, true);
        assertInvalid(BigDecimal.ONE, new BigDecimal("-0.01"), true);
        System.out.println("hidden ABAL migration checks passed");
    }

    private static void assertInvalid(BigDecimal claimAmount, BigDecimal remainingCap,
            boolean approved) {
        try {
            AnnualAllowance.payable(claimAmount, remainingCap, approved);
            throw new AssertionError("invalid allowance input was accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
    }
}
