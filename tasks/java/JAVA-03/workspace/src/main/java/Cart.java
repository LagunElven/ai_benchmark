import java.util.ArrayList;
import java.util.List;

public final class Cart {
    public record CartLine(String sku, boolean expired) {}

    private final List<CartLine> lines = new ArrayList<>();

    public Cart(List<CartLine> initialLines) {
        lines.addAll(initialLines);
    }

    public void removeExpired() {
        for (CartLine line : lines) {
            if (line.expired()) {
                lines.remove(line);
            }
        }
    }

    public List<CartLine> lines() {
        return List.copyOf(lines);
    }
}
