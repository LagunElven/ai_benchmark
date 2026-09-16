import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public final class LedgerApi {
    private LedgerApi() {}

    public static Map<String, Object> adjust(Map<String, Object> request) {
        if (request == null || !(request.get("entries") instanceof List<?> rawEntries)) {
            throw new IllegalArgumentException("balance and entries are required");
        }
        BigDecimal balance = parseAmount(request.get("balance"));
        List<LedgerService.Entry> entries = new ArrayList<>();
        for (Object rawEntry : rawEntries) {
            if (!(rawEntry instanceof Map<?, ?> entry)
                    || !(entry.get("code") instanceof String code)) {
                throw new IllegalArgumentException("malformed ledger entry");
            }
            entries.add(new LedgerService.Entry(parseAmount(entry.get("amount")), code));
        }
        BigDecimal result = LedgerService.applyBatch(balance, entries);
        return Map.of("status", "OK", "balance", result.toPlainString());
    }

    private static BigDecimal parseAmount(Object value) {
        if (!(value instanceof String text)) {
            throw new IllegalArgumentException("amount must be a decimal string");
        }
        try {
            return new BigDecimal(text).setScale(2, RoundingMode.UNNECESSARY);
        } catch (NumberFormatException | ArithmeticException exception) {
            throw new IllegalArgumentException("invalid decimal amount", exception);
        }
    }
}
