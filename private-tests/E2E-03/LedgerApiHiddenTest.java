import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

public final class LedgerApiHiddenTest {
    public static void main(String[] args) {
        Map<String, Object> response = LedgerApi.adjust(Map.of(
                "balance", "0.10",
                "entries", List.of(
                        Map.of("amount", "0.20", "code", "C"),
                        Map.of("amount", "0.05", "code", "D"),
                        Map.of("amount", "1.00", "code", "N"))));
        if (!"0.25".equals(response.get("balance"))) {
            throw new AssertionError("ordered batch mismatch: " + response);
        }
        if (!new BigDecimal("-5.00").equals(LedgerService.applyBatch(
                new BigDecimal("0.00"),
                List.of(new LedgerService.Entry(new BigDecimal("10.00"), "D"),
                        new LedgerService.Entry(new BigDecimal("5.00"), "C"))))) {
            throw new AssertionError("debit/credit order mismatch");
        }
        if (!new BigDecimal("100.00").equals(LedgerService.apply(
                new BigDecimal("100.00"), new BigDecimal("2.00"), "N"))) {
            throw new AssertionError("no-op code mismatch");
        }
        expectFailure(() -> LedgerService.applyBatch(
                new BigDecimal("10.00"),
                List.of(new LedgerService.Entry(new BigDecimal("1.00"), "X"))));
        expectFailure(() -> LedgerApi.adjust(Map.of(
                "balance", "10.00",
                "entries", List.of(Map.of("amount", "-1.00", "code", "C")))));
        expectFailure(() -> LedgerApi.adjust(Map.of(
                "balance", "10.00",
                "entries", List.of(Map.of("amount", "1.00", "code", "X")))));
        System.out.println("hidden e2e-03 checks passed");
    }

    private static void expectFailure(Runnable action) {
        try {
            action.run();
        } catch (IllegalArgumentException expected) {
            return;
        }
        throw new AssertionError("invalid ledger input was accepted");
    }
}
