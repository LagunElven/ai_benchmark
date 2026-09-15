import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

public final class InventoryHiddenTest {
    public static void main(String[] args) throws Exception {
        var inventory = new Inventory(Map.of("SKU-1", 1));
        var executor = Executors.newFixedThreadPool(16);
        var start = new CountDownLatch(1);
        var done = new CountDownLatch(40);
        var successes = new AtomicInteger();
        for (int index = 0; index < 40; index++) {
            executor.submit(() -> {
                try {
                    start.await();
                    if (inventory.reserve("SKU-1", 1)) successes.incrementAndGet();
                } catch (InterruptedException error) {
                    Thread.currentThread().interrupt();
                } finally {
                    done.countDown();
                }
            });
        }
        start.countDown();
        done.await();
        executor.shutdownNow();
        if (successes.get() != 1 || inventory.available("SKU-1") != 0) {
            throw new AssertionError("concurrent reservations oversold stock");
        }
        if (inventory.reserve(null, 1) || inventory.reserve("missing", 1)) {
            throw new AssertionError("invalid SKU accepted");
        }
        System.out.println("hidden inventory checks passed");
    }
}
