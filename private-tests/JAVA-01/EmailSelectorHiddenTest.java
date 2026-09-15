import java.util.Arrays;
import java.util.List;

public final class EmailSelectorHiddenTest {
    public static void main(String[] args) {
        if (EmailSelector.firstUsable(null).isPresent()) {
            throw new AssertionError("null list should be empty");
        }
        var values = Arrays.asList(null, "  ", " Bob@Example.test ", "later@example.test");
        var result = EmailSelector.firstUsable(values);
        if (!result.isPresent() || !"bob@example.test".equals(result.get())) {
            throw new AssertionError("null and blank entries were not skipped");
        }
        if (EmailSelector.firstUsable(List.of("", " \t ")).isPresent()) {
            throw new AssertionError("all blank values should be empty");
        }
        System.out.println("hidden email checks passed");
    }
}
