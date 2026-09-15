public final class StockProjectionPublicTest {
    public static void main(String[] args) {
        var projection = new StockProjection();
        projection.handle(new StockProjection.StockAdded("SKU-1", 5));
        if (projection.available("SKU-1") != 5) throw new AssertionError("stock add failed");
        System.out.println("public stock projection checks passed");
    }
}
