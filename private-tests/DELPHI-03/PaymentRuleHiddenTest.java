public final class PaymentRuleHiddenTest {
    public static void main(String[] args) {
        if (PaymentRule.totalCents(10_000, "card") != 10_200) {
            throw new AssertionError("threshold or case handling is incorrect");
        }
        if (PaymentRule.totalCents(10_001, "CARD") != 10_201) {
            throw new AssertionError("integer surcharge differs from reference");
        }
        try {
            PaymentRule.totalCents(-1, "CARD");
            throw new AssertionError("negative amount accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        System.out.println("hidden Delphi checks passed");
    }
}
