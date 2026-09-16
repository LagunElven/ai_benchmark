import java.math.BigDecimal;

public final class AccountStatusPublicTest {
    public static void main(String[] args) {
        if (AccountStatus.classify(new BigDecimal("0.00"), 0) != AccountStatus.Code.ZERO_BALANCE) {
            throw new AssertionError("zero balance classification failed");
        }
        if (AccountStatus.classify(new BigDecimal("10.00"), 30) != AccountStatus.Code.ACTIVE) {
            throw new AssertionError("30-day boundary is not active");
        }
        System.out.println("public COBOL comprehension checks passed");
    }
}
