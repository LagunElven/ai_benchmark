import java.util.LinkedHashMap;
import java.util.Map;

public final class OrderCreatedUpcaster {
    public record UpcastedEvent(String revision, Map<String, String> payload) {}

    public UpcastedEvent upcast(String revision, Map<String, String> payload) {
        return new UpcastedEvent(revision, payload);
    }
}
