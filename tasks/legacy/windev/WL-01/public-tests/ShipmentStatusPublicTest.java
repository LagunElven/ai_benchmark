public final class ShipmentStatusPublicTest {
    public static void main(String[] args) {
        if (ShipmentStatus.classify(10, 10, 0) != ShipmentStatus.Code.COMPLETE) {
            throw new AssertionError("complete shipment classification failed");
        }
        if (ShipmentStatus.classify(10, 6, 2) != ShipmentStatus.Code.OPEN) {
            throw new AssertionError("open shipment classification failed");
        }
        if (ShipmentStatus.classify(10, 6, 3) != ShipmentStatus.Code.OVERDUE) {
            throw new AssertionError("overdue shipment classification failed");
        }
        System.out.println("public WLanguage comprehension checks passed");
    }
}
