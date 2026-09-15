import java.math.BigDecimal;

public final class BenefitRulePublicTest {
    public static void main(String[] args) {
        if (!new BigDecimal("95.00").equals(BenefitRule.rebate(12, new BigDecimal("100.00")))) {
            throw new AssertionError("documented rebate mismatch");
        }
        System.out.println("public ABAL migration checks passed");
    }
}
