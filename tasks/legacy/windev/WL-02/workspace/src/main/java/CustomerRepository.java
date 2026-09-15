import java.util.ArrayList;
import java.util.List;

public final class CustomerRepository {
    public record Customer(String id, String region, boolean active) {}

    public List<Customer> findActiveByRegion(List<Customer> customers, String region) {
        var result = new ArrayList<Customer>();
        for (var customer : customers) {
            if (customer.active() && customer.region().equals(region)) result.add(customer);
        }
        return result;
    }
}
