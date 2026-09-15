public final class DiscountRule {
    private DiscountRule() {}

    public static int netCents(int grossCents, String classCode) {
        if (grossCents > 100_000 && "P".equals(classCode)) {
            return grossCents - grossCents / 10;
        }
        return grossCents;
    }
}
