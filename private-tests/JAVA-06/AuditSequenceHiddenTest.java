import java.util.Collections;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;

public final class AuditSequenceHiddenTest {
    public static void main(String[] args) throws Exception {
        var sequence = new AuditSequence(100);
        var values = Collections.newSetFromMap(new ConcurrentHashMap<Long, Boolean>());
        var start = new CountDownLatch(1);
        var done = new CountDownLatch(100);
        for (int index = 0; index < 100; index++) {
            new Thread(() -> {
                try { start.await(); values.add(sequence.nextId()); }
                catch (InterruptedException error) { Thread.currentThread().interrupt(); }
                finally { done.countDown(); }
            }).start();
        }
        start.countDown();
        done.await();
        if (values.size() != 100 || !values.contains(100L) || !values.contains(199L)) {
            throw new AssertionError("concurrent sequence contains duplicates or gaps");
        }
        try {
            new AuditSequence(-1);
            throw new AssertionError("negative initial accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        System.out.println("hidden sequence checks passed");
    }
}
