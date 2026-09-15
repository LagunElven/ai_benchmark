public final class OrderProjectionPublicTest {
    public static void main(String[] args) {
        var projection = new OrderProjection();
        projection.apply(new OrderProjection.Event("e-1", "o-1", "PAID"));
        if (!"PAID".equals(projection.status("o-1"))) {
            throw new AssertionError("event was not projected");
        }
        System.out.println("public projection checks passed");
    }
}
