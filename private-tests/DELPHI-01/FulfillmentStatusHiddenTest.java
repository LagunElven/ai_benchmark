public final class FulfillmentStatusHiddenTest {
    public static void main(String[] args) {
        if (FulfillmentStatus.forStock(100, 99, 1) != FulfillmentStatus.Code.REORDER) {
            throw new AssertionError("one available unit should hit the reorder point");
        }
        if (FulfillmentStatus.forStock(0, 0, 0) != FulfillmentStatus.Code.BACKORDER) {
            throw new AssertionError("backorder must take precedence at a zero point");
        }
        assertInvalid(-1, 0, 0);
        assertInvalid(1, -1, 0);
        assertInvalid(1, 0, -1);
        assertInvalid(1, 2, 0);
        System.out.println("hidden Delphi stock checks passed");
    }

    private static void assertInvalid(int onHand, int reserved, int reorderPoint) {
        try {
            FulfillmentStatus.forStock(onHand, reserved, reorderPoint);
            throw new AssertionError("invalid stock values were accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
    }
}
