import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

public final class OrderSummaryService {
    public record Order(String id, String customerId, int cents) {}
    public record Customer(String id, String name) {}
    public record Summary(String orderId, String customerName, int cents) {}

    public static final class Repository {
        private final List<Order> orders;
        private final Map<String, Customer> customers;
        private int queryCount;
        public Repository(List<Order> orders, List<Customer> customers) {
            this.orders = List.copyOf(orders);
            this.customers = new HashMap<>();
            for (Customer customer : customers) this.customers.put(customer.id(), customer);
        }
        public List<Order> findOrders() { queryCount++; return orders; }
        public Customer findCustomer(String id) { queryCount++; return customers.get(id); }
        public Map<String, Customer> findCustomersByIds(Set<String> ids) {
            queryCount++;
            var result = new HashMap<String, Customer>();
            for (String id : ids) if (customers.containsKey(id)) result.put(id, customers.get(id));
            return result;
        }
        public int queryCount() { return queryCount; }
    }

    public List<Summary> load(Repository repository) {
        var result = new ArrayList<Summary>();
        for (Order order : repository.findOrders()) {
            var customer = repository.findCustomer(order.customerId());
            result.add(new Summary(order.id(), customer == null ? "<unknown>" : customer.name(), order.cents()));
        }
        return result;
    }
}
