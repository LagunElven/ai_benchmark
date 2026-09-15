public final class PaymentRule {
    private PaymentRule() {}

    public static int totalCents(int amountCents, String method) {
        if (amountCents < 0) throw new IllegalArgumentException("negative amount");
        if (amountCents > 10_000 && "CARD".equals(method)) {
            return amountCents + amountCents / 50;
        }
        return amountCents;
    }
}
