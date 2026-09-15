import java.math.BigDecimal;

public final class LateFeePublicTest {
    public static void main(String[] args) {
        if (!new BigDecimal("5.00").equals(LateFee.calculate(new BigDecimal("100.00"), 10))) {
            throw new AssertionError("ordinary late fee mismatch");
        }
        System.out.println("public WLanguage migration checks passed");
    }
}
