import java.math.BigDecimal;

public final class TaxBandPublicTest {
    public static void main(String[] args) {
        if (TaxBand.classify(new BigDecimal("500000"), true) != TaxBand.Code.BASIC) {
            throw new AssertionError("basic tax band classification failed");
        }
        if (TaxBand.classify(new BigDecimal("1000000"), true) != TaxBand.Code.BASIC) {
            throw new AssertionError("basic threshold must be inclusive");
        }
        if (TaxBand.classify(new BigDecimal("4000000"), false) != TaxBand.Code.NON_RESIDENT) {
            throw new AssertionError("non-resident classification failed");
        }
        System.out.println("public ABAL comprehension checks passed");
    }
}
