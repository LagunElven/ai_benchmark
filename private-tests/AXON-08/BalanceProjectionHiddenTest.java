import java.util.List;

public final class BalanceProjectionHiddenTest {
    public static void main(String[] args) {
        var projection = new BalanceProjection();
        projection.apply(new BalanceProjection.Credited("stale", 999));
        projection.replay(java.util.Arrays.asList(
                new BalanceProjection.Credited("a", 100),
                new BalanceProjection.Debited("a", 30),
                new BalanceProjection.Debited("a", 100),
                new BalanceProjection.Credited("b", 10),
                null));
        if (projection.balance("stale") != 0 || projection.balance("a") != 70
                || projection.balance("b") != 10) {
            throw new AssertionError("replay did not rebuild deterministic balances");
        }
        projection.replay(List.of(new BalanceProjection.Credited("a", 5)));
        if (projection.balance("a") != 5 || projection.balance("b") != 0) {
            throw new AssertionError("replay retained old state");
        }
        System.out.println("hidden replay checks passed");
    }
}
