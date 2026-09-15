import java.util.concurrent.CompletionStage;
import java.util.concurrent.ScheduledExecutorService;
import java.util.function.Supplier;

public final class AsyncRetry {
    private AsyncRetry() {}

    public static <T> CompletionStage<T> retry(
            Supplier<? extends CompletionStage<T>> operation,
            int maxAttempts,
            ScheduledExecutorService scheduler) {
        return operation.get();
    }
}
