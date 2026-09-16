import java.math.BigDecimal;

public final class AccountStatusHiddenTest {
    public static void main(String[] args) {
        if (AccountStatus.classify(new BigDecimal("0.000"), 365) != AccountStatus.Code.ZERO_BALANCE) {
            throw new AssertionError("zero balance must take precedence");
        }
        if (AccountStatus.classify(new BigDecimal("10.01"), 31) != AccountStatus.Code.DELINQUENT) {
            throw new AssertionError("overdue boundary is wrong");
        }
        if (AccountStatus.classify(new BigDecimal("10.01"), 29) != AccountStatus.Code.ACTIVE) {
            throw new AssertionError("active classification is wrong");
        }
        for (int days : new int[] {-1}) {
            try {
                AccountStatus.classify(BigDecimal.ONE, days);
                throw new AssertionError("negative days were accepted");
            } catch (IllegalArgumentException expected) {
                // expected
            }
        }
        try {
            AccountStatus.classify(null, 0);
            throw new AssertionError("null balance was accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        try {
            AccountStatus.classify(new BigDecimal("-0.01"), 0);
            throw new AssertionError("negative balance was accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        System.out.println("hidden COBOL comprehension checks passed");
    }
}
