import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

public final class VersionedProfileHiddenTest {
    public static void main(String[] args) throws Exception {
        var profile = new VersionedProfile("Ada", "ada@example.test");
        if (profile.update(1, "stale", null) || profile.version() != 0
                || !"Ada".equals(profile.name())) {
            throw new AssertionError("stale update changed profile");
        }
        var start = new CountDownLatch(1);
        var done = new CountDownLatch(2);
        var successes = new AtomicInteger();
        for (String name : new String[] {"first", "second"}) {
            new Thread(() -> {
                try { start.await(); if (profile.update(0, name, null)) successes.incrementAndGet(); }
                catch (InterruptedException error) { Thread.currentThread().interrupt(); }
                finally { done.countDown(); }
            }).start();
        }
        start.countDown();
        done.await();
        if (successes.get() != 1 || profile.version() != 1) {
            throw new AssertionError("concurrent stale updates were both accepted");
        }
        System.out.println("hidden versioned-update checks passed");
    }
}
