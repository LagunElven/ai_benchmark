import java.math.BigDecimal;

public final class CustomerBalancePublicTest {
    public static void main(String[] args) {
        BigDecimal actual = CustomerBalance.calculate(new BigDecimal("100.00"), new BigDecimal("20.00"));
        if (!new BigDecimal("80.00").equals(actual)) {
            throw new AssertionError("balance mismatch: " + actual);
        }
        System.out.println("public Delphi migration checks passed");
    }
}
