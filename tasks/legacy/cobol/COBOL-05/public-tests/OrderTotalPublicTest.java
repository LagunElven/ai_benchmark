import java.math.BigDecimal;

public final class OrderTotalPublicTest {
    public static void main(String[] args) {
        BigDecimal actual = OrderTotal.calculate(new BigDecimal("100.00"), new BigDecimal("20.00"));
        if (!new BigDecimal("120.00").equals(actual)) {
            throw new AssertionError("ordinary total mismatch: " + actual);
        }
        System.out.println("public COBOL migration checks passed");
    }
}
