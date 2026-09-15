import java.util.Map;

public final class CustomerDirtyUpdatePublicTest {
    public static void main(String[] args) {
        var customer = new CustomerDirtyUpdate.Customer("Ada", "ACTIVE", 4);
        CustomerDirtyUpdate.apply(customer, Map.of("name", "Ada Lovelace"));
        if (!"Ada Lovelace".equals(customer.name()) || !"ACTIVE".equals(customer.status())
                || customer.points() != 4) throw new AssertionError("dirty update lost fields");
        System.out.println("public dirty-checking checks passed");
    }
}
