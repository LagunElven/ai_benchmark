import java.util.List;
import java.util.Optional;

public final class EmailSelector {
    private EmailSelector() {}

    public static Optional<String> firstUsable(List<String> emails) {
        return Optional.of(emails.stream()
                .filter(value -> !value.isBlank())
                .findFirst()
                .orElse(""));
    }
}
