public final class OptimisticStockPublicTest {
    public static void main(String[] args) {
        OptimisticStock stock = new OptimisticStock(10);
        OptimisticStock.Snapshot first = stock.read();
        stock.update(first, 9);
        boolean conflict = false;
        try {
            stock.update(first, 8);
        } catch (OptimisticStock.ConflictException expected) {
            conflict = true;
        }
        if (!conflict || stock.read().quantity() != 9 || stock.read().version() != 1) {
            throw new AssertionError("stale update was accepted");
        }
        System.out.println("public optimistic locking checks passed");
    }
}
