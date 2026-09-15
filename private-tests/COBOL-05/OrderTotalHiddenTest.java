import java.math.BigDecimal;

public final class OrderTotalHiddenTest {
    public static void main(String[] args) {
        if (!new BigDecimal("9999999.99").equals(
                OrderTotal.calculate(new BigDecimal("9999999.00"), new BigDecimal("10.00")))) {
            throw new AssertionError("COBOL cap was not preserved");
        }
        BigDecimal actual = OrderTotal.calculate(new BigDecimal("0.10"), new BigDecimal("0.20"));
        if (!new BigDecimal("0.30").equals(actual) || actual.scale() != 2) {
            throw new AssertionError("decimal scale/arithmetic mismatch: " + actual);
        }
        System.out.println("hidden COBOL migration checks passed");
    }
}
