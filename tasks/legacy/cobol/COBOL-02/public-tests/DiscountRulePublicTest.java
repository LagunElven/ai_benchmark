public final class DiscountRulePublicTest {
    public static void main(String[] args) {
        if (DiscountRule.netCents(200_000, "P") != 180_000) {
            throw new AssertionError("preferred discount missing");
        }
        if (DiscountRule.netCents(200_000, "N") != 200_000) {
            throw new AssertionError("non-preferred customer was discounted");
        }
        System.out.println("public COBOL rule checks passed");
    }
}
