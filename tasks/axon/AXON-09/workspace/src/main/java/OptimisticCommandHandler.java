public final class OptimisticCommandHandler {
    public static final class ConflictException extends RuntimeException {
        public ConflictException(String message) { super(message); }
    }

    public static final class Aggregate {
        private long version;
        private int balance;
        public Aggregate(long version, int balance) { this.version = version; this.balance = balance; }
        public long version() { return version; }
        public int balance() { return balance; }
    }

    public void apply(Aggregate aggregate, long expectedVersion, int delta) {
        aggregate.balance += delta;
        aggregate.version++;
    }

    public void applyWithRetry(Aggregate aggregate, int delta, int maxAttempts) {
        apply(aggregate, aggregate.version(), delta);
    }
}
