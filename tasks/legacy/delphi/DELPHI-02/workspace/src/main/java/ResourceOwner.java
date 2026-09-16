import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public final class ResourceOwner implements AutoCloseable {
    private final List<String> active;
    private boolean closed;
    private int releaseCount;

    public ResourceOwner(List<String> names) {
        if (names == null) {
            throw new IllegalArgumentException("names must not be null");
        }
        this.active = new ArrayList<>(names);
    }

    public List<String> activeNames() {
        return Collections.unmodifiableList(new ArrayList<>(active));
    }

    @Override
    public void close() {
        if (closed) return;
        if (!active.isEmpty()) {
            active.remove(0);
            releaseCount++;
        }
        closed = true;
    }

    public int releaseCount() {
        return releaseCount;
    }

    public boolean isClosed() {
        return closed;
    }
}
