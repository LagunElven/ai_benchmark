import java.util.List;

public final class BalanceProjectionPublicTest {
    public static void main(String[] args) {
        var projection = new BalanceProjection();
        projection.replay(List.of(new BalanceProjection.Credited("a", 100)));
        if (projection.balance("a") != 100) throw new AssertionError("replay failed");
        System.out.println("public replay checks passed");
    }
}
