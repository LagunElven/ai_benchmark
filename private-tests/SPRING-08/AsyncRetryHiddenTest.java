import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public final class AsyncRetryHiddenTest {
    public static void main(String[] args) {
        var scheduler = Executors.newSingleThreadScheduledExecutor();
        try {
            var attempts = new AtomicInteger();
            var value = AsyncRetry.retry(() -> {
                if (attempts.incrementAndGet() < 3) {
                    return CompletableFuture.failedFuture(new IllegalStateException("transient"));
                }
                return CompletableFuture.completedFuture("ready");
            }, 3, scheduler).toCompletableFuture().orTimeout(2, TimeUnit.SECONDS).join();
            if (!"ready".equals(value) || attempts.get() != 3) {
                throw new AssertionError("transient errors were not retried");
            }
            var permanent = new AtomicInteger();
            try {
                AsyncRetry.retry(() -> {
                    permanent.incrementAndGet();
                    return CompletableFuture.failedFuture(new RuntimeException("nope"));
                }, 2, scheduler).toCompletableFuture().orTimeout(2, TimeUnit.SECONDS).join();
                throw new AssertionError("permanent error was swallowed");
            } catch (Exception expected) {
                if (permanent.get() != 2) throw new AssertionError("wrong retry count");
            }
        } finally { scheduler.shutdownNow(); }
        System.out.println("hidden retry checks passed");
    }
}
