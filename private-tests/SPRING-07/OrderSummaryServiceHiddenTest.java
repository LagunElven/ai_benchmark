import java.util.List;

public final class OrderSummaryServiceHiddenTest {
    public static void main(String[] args) {
        var repository = new OrderSummaryService.Repository(
                List.of(new OrderSummaryService.Order("o-1", "c-1", 100),
                        new OrderSummaryService.Order("o-2", "c-2", 200),
                        new OrderSummaryService.Order("o-3", "missing", 300)),
                List.of(new OrderSummaryService.Customer("c-1", "Ada"),
                        new OrderSummaryService.Customer("c-2", "Bob")));
        var summaries = new OrderSummaryService().load(repository);
        if (summaries.size() != 3 || !"<unknown>".equals(summaries.get(2).customerName())) {
            throw new AssertionError("unknown customer or order order is wrong");
        }
        if (repository.queryCount() > 2) throw new AssertionError("N+1 customer queries remain");
        if (!new OrderSummaryService().load(null).isEmpty()) {
            throw new AssertionError("null repository should be empty");
        }
        System.out.println("hidden N+1 checks passed");
    }
}
