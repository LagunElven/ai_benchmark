public final class OptimisticCommandHandlerHiddenTest {
    public static void main(String[] args) {
        var handler = new OptimisticCommandHandler();
        var aggregate = new OptimisticCommandHandler.Aggregate(2, 10);
        try {
            handler.apply(aggregate, 1, 5);
            throw new AssertionError("stale version accepted");
        } catch (OptimisticCommandHandler.ConflictException expected) {
            // expected
        }
        if (aggregate.version() != 2 || aggregate.balance() != 10) {
            throw new AssertionError("stale command changed aggregate");
        }
        handler.applyWithRetry(aggregate, 5, 2);
        if (aggregate.version() != 3 || aggregate.balance() != 15) {
            throw new AssertionError("retry did not use current version");
        }
        try {
            handler.applyWithRetry(aggregate, 1, 0);
            throw new AssertionError("invalid retry limit accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        System.out.println("hidden optimistic-lock checks passed");
    }
}
