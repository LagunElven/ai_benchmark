import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

public final class PostedSalesHiddenTest {
    public static void main(String[] args) {
        var records = new ArrayList<>(List.of(
                "A0001|0.10|P", "A0002|-1.25|P", "A0003|2|p", "A0004|3.4|P"));
        var before = new ArrayList<>(records);
        var actual = PostedSales.totalPosted(records);
        if (!new BigDecimal("2.25").equals(actual) || !before.equals(records)) {
            throw new AssertionError("signed or scaled sequential total is wrong");
        }
        if (!new BigDecimal("0.00").equals(PostedSales.totalPosted(null))) {
            throw new AssertionError("null records should total zero");
        }
        for (String malformed : List.of(
                "A0001|1.234|P", "|1.00|P", "A0001||P", "A0001|1.00", "A0001|nope|P")) {
            try {
                PostedSales.totalPosted(List.of(malformed));
                throw new AssertionError("malformed record was accepted: " + malformed);
            } catch (IllegalArgumentException expected) {
                // expected
            }
        }
        if (!new BigDecimal("10000000.00").equals(PostedSales.totalPosted(
                List.of("A0001|9999999.99|P", "A0002|0.01|P")))) {
            throw new AssertionError("large packed-decimal total lost precision");
        }
        System.out.println("hidden COBOL sequential checks passed");
    }
}
