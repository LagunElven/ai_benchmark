import java.math.BigDecimal;

public final class BenefitRuleHiddenTest {
    public static void main(String[] args) {
        if (!new BigDecimal("100.00").equals(BenefitRule.rebate(11, new BigDecimal("100.00")))) {
            throw new AssertionError("non-eligible member changed");
        }
        BigDecimal actual = BenefitRule.rebate(12, new BigDecimal("0.10"));
        if (!new BigDecimal("0.10").equals(actual) || actual.scale() != 2) {
            throw new AssertionError("rebate decimal scale mismatch: " + actual);
        }
        System.out.println("hidden ABAL migration checks passed");
    }
}
