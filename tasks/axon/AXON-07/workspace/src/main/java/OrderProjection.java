import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public final class OrderProjection {
    public record Event(String id, String orderId, String status) {}

    private final Set<String> appliedEventIds = new HashSet<>();
    private final Map<String, String> statuses = new HashMap<>();

    public void apply(Event event) {
        if (event == null || event.id() == null || event.id().isBlank()
                || event.orderId() == null || event.orderId().isBlank()) {
            return;
        }
        statuses.put(event.orderId(), event.status());
        appliedEventIds.add(event.id());
    }

    public String status(String orderId) {
        return statuses.get(orderId);
    }
}
