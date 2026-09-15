import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;

public final class AsyncRetryPublicTest {
    public static void main(String[] args) {
        var scheduler = Executors.newSingleThreadScheduledExecutor();
        try {
            var value = AsyncRetry.retry(() -> CompletableFuture.completedFuture("ok"), 3, scheduler)
                    .toCompletableFuture().join();
            if (!"ok".equals(value)) throw new AssertionError("success was not returned");
        } finally { scheduler.shutdownNow(); }
        System.out.println("public retry checks passed");
    }
}
