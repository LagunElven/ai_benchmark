import java.math.BigDecimal;
import java.util.List;

public final class PostedSalesPublicTest {
    public static void main(String[] args) {
        var records = List.of("A0001|10.00|P", "A0002|2.35|V", "A0003|1.00|P");
        var actual = PostedSales.totalPosted(records);
        if (!new BigDecimal("11.00").equals(actual)) {
            throw new AssertionError("posted sales total mismatch: " + actual);
        }
        System.out.println("public COBOL sequential checks passed");
    }
}
