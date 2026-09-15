import java.util.LinkedHashMap;
import java.util.Map;

public final class OrderEventUpcaster {
    public record UpcastedEvent(String revision, Map<String, String> payload) {}

    public UpcastedEvent upcast(String revision, Map<String, String> payload) {
        if (!"2".equals(revision)) {
            throw new IllegalArgumentException("unsupported revision: " + revision);
        }
        return new UpcastedEvent(revision, payload);
    }
}
