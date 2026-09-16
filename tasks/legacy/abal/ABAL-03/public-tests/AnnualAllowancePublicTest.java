import java.math.BigDecimal;

public final class AnnualAllowancePublicTest {
    public static void main(String[] args) {
        if (!new BigDecimal("80.00").equals(AnnualAllowance.payable(
                new BigDecimal("80.00"), new BigDecimal("100.00"), true))) {
            throw new AssertionError("approved claim below cap is wrong");
        }
        if (!new BigDecimal("0.00").equals(AnnualAllowance.payable(
                new BigDecimal("80.00"), new BigDecimal("100.00"), false))) {
            throw new AssertionError("unapproved claim was paid");
        }
        System.out.println("public ABAL migration checks passed");
    }
}
