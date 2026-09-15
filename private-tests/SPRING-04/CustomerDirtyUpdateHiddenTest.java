import java.util.HashMap;
import java.util.Map;

public final class CustomerDirtyUpdateHiddenTest {
    public static void main(String[] args) {
        var customer = new CustomerDirtyUpdate.Customer("Ada", "ACTIVE", 4);
        var patch = new HashMap<String, Object>();
        patch.put("status", null);
        CustomerDirtyUpdate.apply(customer, patch);
        if (customer.name() == null || customer.points() != 4 || customer.status() != null) {
            throw new AssertionError("explicit null or untouched fields were mishandled");
        }
        try {
            CustomerDirtyUpdate.apply(customer, Map.of("unknown", "x"));
            throw new AssertionError("unknown dirty field accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        try {
            CustomerDirtyUpdate.apply(customer, Map.of("points", "four"));
            throw new AssertionError("incompatible field type accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        System.out.println("hidden dirty-checking checks passed");
    }
}
