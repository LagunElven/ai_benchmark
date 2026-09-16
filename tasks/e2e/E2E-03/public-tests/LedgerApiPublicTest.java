import java.util.List;
import java.util.Map;

public final class LedgerApiPublicTest {
    public static void main(String[] args) {
        Map<String, Object> request = Map.of(
                "balance", "100.00",
                "entries", List.of(
                        Map.of("amount", "25.00", "code", "C"),
                        Map.of("amount", "5.00", "code", "D")));
        Map<String, Object> response = LedgerApi.adjust(request);
        if (!"OK".equals(response.get("status")) || !"120.00".equals(response.get("balance"))) {
            throw new AssertionError("legacy ledger contract mismatch: " + response);
        }
        System.out.println("public e2e-03 checks passed");
    }
}
