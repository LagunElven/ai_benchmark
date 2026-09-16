import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;

public final class LedgerService {
    public record Entry(BigDecimal amount, String code) {}

    private LedgerService() {}

    public static BigDecimal apply(BigDecimal balance, BigDecimal amount, String code) {
        if (balance == null || amount == null || amount.signum() < 0 || code == null) {
            throw new IllegalArgumentException("invalid ledger entry");
        }
        BigDecimal normalizedBalance = balance.setScale(2, RoundingMode.UNNECESSARY);
        BigDecimal normalizedAmount = amount.setScale(2, RoundingMode.UNNECESSARY);
        if ("C".equals(code)) return normalizedBalance.add(normalizedAmount);
        if ("D".equals(code)) return normalizedBalance.subtract(normalizedAmount);
        if ("N".equals(code)) return normalizedBalance;
        throw new IllegalArgumentException("unknown ledger code: " + code);
    }

    public static BigDecimal applyBatch(BigDecimal balance, List<Entry> entries) {
        return balance;
    }
}
