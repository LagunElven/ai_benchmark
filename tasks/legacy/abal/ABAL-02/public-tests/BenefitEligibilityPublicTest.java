public final class BenefitEligibilityPublicTest {
    public static void main(String[] args) {
        if (!BenefitEligibility.eligible(200_000, true, false)) {
            throw new AssertionError("retired claimant should be eligible");
        }
        if (BenefitEligibility.eligible(200_000, false, false)) {
            throw new AssertionError("unqualified claimant was accepted");
        }
        System.out.println("public ABAL checks passed");
    }
}
