import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

public final class LedgerAdjusterHiddenTest {
    public static void main(String[] args) {
        if (!new BigDecimal("75.00").equals(
                LedgerAdjuster.apply(new BigDecimal("100.00"), new BigDecimal("25"), "D"))) {
            throw new AssertionError("debit behavior is missing");
        }
        if (!new BigDecimal("100.00").equals(
                LedgerAdjuster.apply(new BigDecimal("100"), new BigDecimal("25"), "N"))) {
            throw new AssertionError("no-op behavior is missing");
        }
        var entries = new ArrayList<>(List.of(
                new LedgerAdjuster.Entry(new BigDecimal("0.10"), "C"),
                new LedgerAdjuster.Entry(new BigDecimal("0.05"), "D"),
                new LedgerAdjuster.Entry(new BigDecimal("99.95"), "N")));
        var before = new ArrayList<>(entries);
        if (!new BigDecimal("100.05").equals(
                LedgerAdjuster.applyBatch(new BigDecimal("100.00"), entries)) || !before.equals(entries)) {
            throw new AssertionError("ordered batch arithmetic or input immutability failed");
        }
        if (!new BigDecimal("100.00").equals(
                LedgerAdjuster.applyBatch(new BigDecimal("100"), null))) {
            throw new AssertionError("null batch should preserve normalized balance");
        }
        for (LedgerAdjuster.Entry invalid : List.of(
                new LedgerAdjuster.Entry(BigDecimal.ONE, "X"),
                new LedgerAdjuster.Entry(new BigDecimal("-0.01"), "C"),
                new LedgerAdjuster.Entry(new BigDecimal("1.001"), "C"),
                new LedgerAdjuster.Entry(null, "C"))) {
            try {
                LedgerAdjuster.applyBatch(BigDecimal.ZERO, List.of(invalid));
                throw new AssertionError("invalid batch entry was accepted");
            } catch (IllegalArgumentException expected) {
                // expected
            }
        }
        try {
            LedgerAdjuster.apply(null, BigDecimal.ONE, "C");
            throw new AssertionError("null balance was accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        System.out.println("hidden COBOL maintenance checks passed");
    }
}
