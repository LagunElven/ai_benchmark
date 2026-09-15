public final class OptimisticStock {
    public record Snapshot(int quantity, long version) {}

    public static final class ConflictException extends RuntimeException {
        public ConflictException(long expected, long actual) {
            super("stale version: expected " + expected + ", actual " + actual);
        }
    }

    private int quantity;
    private long version;

    public OptimisticStock(int quantity) {
        this.quantity = quantity;
    }

    public synchronized Snapshot read() {
        return new Snapshot(quantity, version);
    }

    public synchronized void update(Snapshot expected, int replacementQuantity) {
        quantity = replacementQuantity;
        version++;
    }
}
