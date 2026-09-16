public final class ShipmentStatusHiddenTest {
    public static void main(String[] args) {
        if (ShipmentStatus.classify(0, 0, 365) != ShipmentStatus.Code.COMPLETE) {
            throw new AssertionError("completion must take precedence over lateness");
        }
        if (ShipmentStatus.classify(8, 7, 3) != ShipmentStatus.Code.OVERDUE) {
            throw new AssertionError("remaining overdue shipment was not detected");
        }
        assertInvalid(-1, 0, 0);
        assertInvalid(1, -1, 0);
        assertInvalid(1, 2, 0);
        assertInvalid(1, 0, -1);
        System.out.println("hidden WLanguage comprehension checks passed");
    }

    private static void assertInvalid(int orderedUnits, int shippedUnits, int daysSincePromise) {
        try {
            ShipmentStatus.classify(orderedUnits, shippedUnits, daysSincePromise);
            throw new AssertionError("invalid shipment values were accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
    }
}
