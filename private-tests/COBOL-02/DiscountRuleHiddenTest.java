public final class DiscountRuleHiddenTest {
    public static void main(String[] args) {
        if (DiscountRule.netCents(100_000, "P") != 90_000) {
            throw new AssertionError("threshold must be inclusive");
        }
        if (DiscountRule.netCents(99_999, "P") != 99_999) {
            throw new AssertionError("amount below threshold was discounted");
        }
        if (DiscountRule.netCents(100_000, null) != 100_000) {
            throw new AssertionError("null class code was discounted");
        }
        if (DiscountRule.netCents(100_001, "P") != 90_001) {
            throw new AssertionError("integer truncation differs from COBOL reference");
        }
        System.out.println("hidden COBOL rule checks passed");
    }
}
