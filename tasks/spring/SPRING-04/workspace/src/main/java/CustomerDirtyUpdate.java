import java.util.Map;

public final class CustomerDirtyUpdate {
    public static final class Customer {
        private String name;
        private String status;
        private int points;
        public Customer(String name, String status, int points) {
            this.name = name; this.status = status; this.points = points;
        }
        public String name() { return name; }
        public String status() { return status; }
        public int points() { return points; }
        private void name(String value) { name = value; }
        private void status(String value) { status = value; }
        private void points(int value) { points = value; }
    }

    public static void apply(Customer customer, Map<String, Object> dirtyFields) {
        customer.name((String) dirtyFields.get("name"));
        customer.status((String) dirtyFields.get("status"));
        customer.points((Integer) dirtyFields.getOrDefault("points", 0));
    }
}
