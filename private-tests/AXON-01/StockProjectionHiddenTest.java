public final class StockProjectionHiddenTest {
    public static void main(String[] args) {
        var projection = new StockProjection();
        projection.handle(new StockProjection.StockAdded("SKU-1", 5));
        projection.handle(new StockProjection.StockRemoved("SKU-1", 2));
        if (projection.available("SKU-1") != 3) throw new AssertionError("stock removal failed");
        projection.handle(new StockProjection.StockRemoved("SKU-1", 4));
        if (projection.available("SKU-1") != 3) throw new AssertionError("negative stock allowed");
        projection.handle(new StockProjection.StockAdded("", 2));
        projection.handle(new StockProjection.StockAdded("SKU-1", 0));
        projection.handle(new Object());
        projection.handle(null);
        if (projection.available("") != 0 || projection.available("SKU-1") != 3) {
            throw new AssertionError("invalid event was applied");
        }
        System.out.println("hidden stock projection checks passed");
    }
}
