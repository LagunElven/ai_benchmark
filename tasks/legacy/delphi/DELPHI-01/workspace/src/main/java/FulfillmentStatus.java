public final class FulfillmentStatus {
    public enum Code { BACKORDER, REORDER, READY }

    private FulfillmentStatus() {}

    public static Code forStock(int onHand, int reserved, int reorderPoint) {
        if (onHand < 0 || reserved < 0 || reorderPoint < 0 || reserved > onHand) {
            throw new IllegalArgumentException("invalid stock values");
        }
        int available = onHand - reserved;
        if (available <= reorderPoint) return Code.REORDER;
        if (available == 0) return Code.BACKORDER;
        return Code.READY;
    }
}
