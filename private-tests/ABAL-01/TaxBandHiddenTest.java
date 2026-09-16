import java.math.BigDecimal;

public final class TaxBandHiddenTest {
    public static void main(String[] args) {
        if (TaxBand.classify(new BigDecimal("1000000.00"), true) != TaxBand.Code.BASIC) {
            throw new AssertionError("decimal representation changed the boundary");
        }
        if (TaxBand.classify(new BigDecimal("1000000.01"), true) != TaxBand.Code.STANDARD) {
            throw new AssertionError("standard lower boundary is wrong");
        }
        if (TaxBand.classify(new BigDecimal("3000000"), true) != TaxBand.Code.STANDARD) {
            throw new AssertionError("standard upper boundary is wrong");
        }
        if (TaxBand.classify(BigDecimal.ZERO, true) != TaxBand.Code.BASIC) {
            throw new AssertionError("zero income classification failed");
        }
        try {
            TaxBand.classify(null, true);
            throw new AssertionError("null income was accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        try {
            TaxBand.classify(new BigDecimal("-0.01"), true);
            throw new AssertionError("negative income was accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        System.out.println("hidden ABAL comprehension checks passed");
    }
}
