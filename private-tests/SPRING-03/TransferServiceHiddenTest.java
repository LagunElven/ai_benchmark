import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

public final class TransferServiceHiddenTest {
    public static void main(String[] args) throws Exception {
        var accounts = new TransferService.Accounts(Map.of("a", 1_000, "b", 0));
        accounts.rejectCreditsFor("b");
        if (new TransferService().transfer(accounts, "a", "b", 250)) {
            throw new AssertionError("rejected credit reported success");
        }
        if (accounts.balance("a") != 1_000 || accounts.balance("b") != 0) {
            throw new AssertionError("failed transfer was not rolled back");
        }
        if (new TransferService().transfer(accounts, "a", "a", 1)
                || new TransferService().transfer(accounts, "missing", "b", 1)
                || new TransferService().transfer(accounts, "a", "b", 0)) {
            throw new AssertionError("invalid transfer accepted");
        }
        var concurrent = new TransferService.Accounts(Map.of("a", 1_000, "b", 0, "c", 0));
        var start = new CountDownLatch(1);
        var done = new CountDownLatch(2);
        var successes = new AtomicInteger();
        for (String destination : new String[] {"b", "c"}) {
            new Thread(() -> {
                try {
                    start.await();
                    if (new TransferService().transfer(concurrent, "a", destination, 600)) {
                        successes.incrementAndGet();
                    }
                } catch (InterruptedException error) {
                    Thread.currentThread().interrupt();
                } finally {
                    done.countDown();
                }
            }).start();
        }
        start.countDown();
        done.await();
        if (successes.get() != 1 || concurrent.balance("a") != 400
                || concurrent.balance("b") + concurrent.balance("c") != 600) {
            throw new AssertionError("concurrent transfers were not atomic");
        }
        System.out.println("hidden transfer checks passed");
    }
}
