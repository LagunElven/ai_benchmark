public final class BenefitEligibility {
    private BenefitEligibility() {}

    public static boolean eligible(int incomeCents, boolean retired, boolean disabled) {
        if (incomeCents < 0) throw new IllegalArgumentException("negative income");
        return retired && disabled && incomeCents < 250_000;
    }
}
