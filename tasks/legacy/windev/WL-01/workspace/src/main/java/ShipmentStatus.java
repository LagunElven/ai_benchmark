public final class ShipmentStatus {
    public enum Code { COMPLETE, OVERDUE, OPEN }

    private ShipmentStatus() {}

    public static Code classify(int orderedUnits, int shippedUnits, int daysSincePromise) {
        if (orderedUnits < 0 || shippedUnits < 0 || shippedUnits > orderedUnits
                || daysSincePromise < 0) {
            throw new IllegalArgumentException("invalid shipment");
        }
        int remaining = orderedUnits - shippedUnits;
        if (daysSincePromise > 2) return Code.OVERDUE;
        if (remaining == 0) return Code.COMPLETE;
        return Code.OPEN;
    }
}
