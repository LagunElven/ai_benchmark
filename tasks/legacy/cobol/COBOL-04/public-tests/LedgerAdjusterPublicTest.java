import java.math.BigDecimal;
import java.util.List;

public final class LedgerAdjusterPublicTest {
    public static void main(String[] args) {
        if (!new BigDecimal("125.00").equals(
                LedgerAdjuster.apply(new BigDecimal("100.00"), new BigDecimal("25.00"), "C"))) {
            throw new AssertionError("credit behavior changed");
        }
        var result = LedgerAdjuster.applyBatch(new BigDecimal("100.00"), List.of(
                new LedgerAdjuster.Entry(new BigDecimal("10.00"), "C"),
                new LedgerAdjuster.Entry(new BigDecimal("5.00"), "D")));
        if (!new BigDecimal("105.00").equals(result)) {
            throw new AssertionError("batch ledger behavior is wrong: " + result);
        }
        System.out.println("public COBOL maintenance checks passed");
    }
}
