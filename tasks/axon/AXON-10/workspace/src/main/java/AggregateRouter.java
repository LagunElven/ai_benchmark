import java.util.HashMap;
import java.util.Map;

public final class AggregateRouter {
    public record Command(String type, String id, int amount) {}
    private final Map<String, Integer> totals = new HashMap<>();

    public int dispatch(Command command) {
        return totals.merge(command.id(), command.amount(), Integer::sum);
    }

    public int total(String type, String id) { return totals.getOrDefault(id, 0); }
}
