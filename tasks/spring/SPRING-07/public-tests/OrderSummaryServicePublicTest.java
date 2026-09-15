import java.util.List;

public final class OrderSummaryServicePublicTest {
    public static void main(String[] args) {
        var repository = new OrderSummaryService.Repository(
                List.of(new OrderSummaryService.Order("o-1", "c-1", 100)),
                List.of(new OrderSummaryService.Customer("c-1", "Ada")));
        var summaries = new OrderSummaryService().load(repository);
        if (summaries.size() != 1 || !"Ada".equals(summaries.get(0).customerName())) {
            throw new AssertionError("summary mapping failed");
        }
        System.out.println("public N+1 checks passed");
    }
}
