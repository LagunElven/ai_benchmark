import java.time.Duration;
import java.time.LocalDateTime;
import java.time.ZoneId;

public final class BillingWindow {
    private BillingWindow() {}

    public static long elapsedHours(LocalDateTime start, LocalDateTime end, ZoneId zone) {
        if (start == null || end == null || zone == null || !end.isAfter(start)) {
            throw new IllegalArgumentException("invalid billing window");
        }
        return Duration.between(start, end).toHours();
    }
}
