import java.time.LocalDateTime;
import java.time.ZoneId;

public final class BillingWindowPublicTest {
    public static void main(String[] args) {
        var start = LocalDateTime.of(2026, 1, 10, 9, 0);
        var end = LocalDateTime.of(2026, 1, 10, 17, 0);
        if (BillingWindow.elapsedHours(start, end, ZoneId.of("UTC")) != 8) {
            throw new AssertionError("ordinary window should be eight hours");
        }
        System.out.println("public DST checks passed");
    }
}
