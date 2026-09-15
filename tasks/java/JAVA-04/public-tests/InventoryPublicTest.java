import java.util.Map;

public final class InventoryPublicTest {
    public static void main(String[] args) {
        var inventory = new Inventory(Map.of("SKU-1", 3));
        if (!inventory.reserve("SKU-1", 2) || inventory.available("SKU-1") != 1) {
            throw new AssertionError("ordinary reservation failed");
        }
        if (inventory.reserve("SKU-1", 2) || inventory.reserve("SKU-1", 0)) {
            throw new AssertionError("invalid reservation accepted");
        }
        System.out.println("public inventory checks passed");
    }
}
