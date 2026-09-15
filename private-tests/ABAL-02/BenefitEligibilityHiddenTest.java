public final class BenefitEligibilityHiddenTest {
    public static void main(String[] args) {
        if (!BenefitEligibility.eligible(250_000, false, true)) {
            throw new AssertionError("income boundary or disabled path is incorrect");
        }
        if (BenefitEligibility.eligible(250_001, false, true)) {
            throw new AssertionError("income above threshold was accepted");
        }
        try {
            BenefitEligibility.eligible(-1, true, false);
            throw new AssertionError("negative income accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        System.out.println("hidden ABAL checks passed");
    }
}
