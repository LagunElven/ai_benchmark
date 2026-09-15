import java.util.concurrent.CountDownLatch;

public final class OrderProjectionHiddenTest {
    public static void main(String[] args) throws Exception {
        var projection = new OrderProjection();
        projection.apply(new OrderProjection.Event("e-1", "o-1", "PAID"));
        projection.apply(new OrderProjection.Event("e-1", "o-1", "CANCELLED"));
        if (!"PAID".equals(projection.status("o-1"))) {
            throw new AssertionError("duplicate event changed projection");
        }
        projection.apply(new OrderProjection.Event("e-2", "o-1", "SHIPPED"));
        if (!"SHIPPED".equals(projection.status("o-1")) || projection.status("missing") != null) {
            throw new AssertionError("distinct event or missing status incorrect");
        }
        var start = new CountDownLatch(1);
        var done = new CountDownLatch(2);
        new Thread(() -> { await(start); projection.apply(new OrderProjection.Event("e-3", "o-2", "A")); done.countDown(); }).start();
        new Thread(() -> { await(start); projection.apply(new OrderProjection.Event("e-4", "o-2", "B")); done.countDown(); }).start();
        start.countDown();
        done.await();
        if (projection.status("o-2") == null) throw new AssertionError("concurrent apply lost state");
        projection.apply(null);
        projection.apply(new OrderProjection.Event(" ", "o-3", "BAD"));
        if (projection.status("o-3") != null) throw new AssertionError("blank id accepted");
        System.out.println("hidden projection checks passed");
    }

    private static void await(CountDownLatch latch) {
        try { latch.await(); } catch (InterruptedException error) { Thread.currentThread().interrupt(); }
    }
}
