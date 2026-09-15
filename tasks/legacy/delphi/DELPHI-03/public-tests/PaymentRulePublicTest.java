public final class PaymentRulePublicTest {
    public static void main(String[] args) {
        if (PaymentRule.totalCents(20_000, "CARD") != 20_400) {
            throw new AssertionError("card surcharge missing");
        }
        if (PaymentRule.totalCents(20_000, "CASH") != 20_000) {
            throw new AssertionError("cash payment changed");
        }
        System.out.println("public Delphi checks passed");
    }
}
