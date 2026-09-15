import java.time.LocalDateTime;
import java.time.ZoneId;

public final class BillingWindowHiddenTest {
    public static void main(String[] args) {
        var zone = ZoneId.of("Europe/Paris");
        var springStart = LocalDateTime.of(2026, 3, 29, 0, 30);
        var springEnd = LocalDateTime.of(2026, 3, 29, 4, 30);
        if (BillingWindow.elapsedHours(springStart, springEnd, zone) != 3) {
            throw new AssertionError("spring-forward gap must not count as a wall hour");
        }
        var autumnStart = LocalDateTime.of(2026, 10, 25, 0, 30);
        var autumnEnd = LocalDateTime.of(2026, 10, 25, 4, 30);
        if (BillingWindow.elapsedHours(autumnStart, autumnEnd, zone) != 5) {
            throw new AssertionError("autumn overlap must count the repeated hour");
        }
        try {
            BillingWindow.elapsedHours(springStart, springStart, zone);
            throw new AssertionError("equal endpoints accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        System.out.println("hidden DST checks passed");
    }
}
