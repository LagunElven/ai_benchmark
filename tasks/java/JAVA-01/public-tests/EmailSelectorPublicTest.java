import java.util.List;

public final class EmailSelectorPublicTest {
    public static void main(String[] args) {
        var result = EmailSelector.firstUsable(List.of("  ", " Alice@Example.test "));
        if (!result.isPresent() || !"alice@example.test".equals(result.get())) {
            throw new AssertionError("first usable address was not normalized");
        }
        System.out.println("public email checks passed");
    }
}
