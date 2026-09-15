public final class OptimisticCommandHandlerPublicTest {
    public static void main(String[] args) {
        var aggregate = new OptimisticCommandHandler.Aggregate(0, 10);
        new OptimisticCommandHandler().apply(aggregate, 0, 5);
        if (aggregate.version() != 1 || aggregate.balance() != 15) {
            throw new AssertionError("command was not applied");
        }
        System.out.println("public optimistic-lock checks passed");
    }
}
