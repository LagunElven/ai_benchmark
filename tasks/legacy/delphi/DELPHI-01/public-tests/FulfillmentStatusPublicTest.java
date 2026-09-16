public final class FulfillmentStatusPublicTest {
    public static void main(String[] args) {
        if (FulfillmentStatus.forStock(20, 5, 10) != FulfillmentStatus.Code.READY) {
            throw new AssertionError("ready stock classification failed");
        }
        if (FulfillmentStatus.forStock(15, 5, 10) != FulfillmentStatus.Code.REORDER) {
            throw new AssertionError("reorder threshold must be inclusive");
        }
        if (FulfillmentStatus.forStock(8, 8, 10) != FulfillmentStatus.Code.BACKORDER) {
            throw new AssertionError("backorder classification failed");
        }
        System.out.println("public Delphi stock checks passed");
    }
}
