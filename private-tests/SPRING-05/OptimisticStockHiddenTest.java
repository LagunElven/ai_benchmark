public final class OptimisticStockHiddenTest {
    public static void main(String[] args) {
        OptimisticStock stock = new OptimisticStock(4);
        OptimisticStock.Snapshot a = stock.read();
        OptimisticStock.Snapshot b = stock.read();
        stock.update(a, 7);
        try {
            stock.update(b, 8);
            throw new AssertionError("second writer must fail");
        } catch (OptimisticStock.ConflictException expected) {
            // expected
        }
        OptimisticStock.Snapshot current = stock.read();
        stock.update(current, 12);
        if (stock.read().quantity() != 12 || stock.read().version() != 2) {
            throw new AssertionError("current update did not increment once");
        }
        System.out.println("hidden optimistic locking checks passed");
    }
}
