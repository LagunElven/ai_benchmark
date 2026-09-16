import java.math.BigDecimal;
import java.util.List;

public final class LedgerAdjuster {
    public record Entry(BigDecimal amount, String code) {}

    private LedgerAdjuster() {}

    public static BigDecimal apply(BigDecimal balance, BigDecimal amount, String code) {
        if ("C".equals(code)) return balance.add(amount);
        return balance;
    }

    public static BigDecimal applyBatch(BigDecimal balance, List<Entry> entries) {
        return balance;
    }
}
