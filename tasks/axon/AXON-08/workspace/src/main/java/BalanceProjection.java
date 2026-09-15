import java.util.HashMap;
import java.util.List;
import java.util.Map;

public final class BalanceProjection {
    public record Credited(String account, int cents) {}
    public record Debited(String account, int cents) {}
    private final Map<String, Integer> balances = new HashMap<>();

    public void apply(Object event) {
        if (event instanceof Credited credited) {
            balances.merge(credited.account(), credited.cents(), Integer::sum);
        }
    }

    public void replay(List<?> events) {
        for (Object event : events) apply(event);
    }

    public int balance(String account) { return balances.getOrDefault(account, 0); }
}
