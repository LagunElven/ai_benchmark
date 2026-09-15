import java.util.List;

public final class CartHiddenTest {
    public static void main(String[] args) {
        Cart allExpired = new Cart(List.of(
                new Cart.CartLine("A", true), new Cart.CartLine("B", true)));
        allExpired.removeExpired();
        if (!allExpired.lines().isEmpty()) throw new AssertionError("all expired lines remain");

        Cart alternating = new Cart(List.of(
                new Cart.CartLine("A", true), new Cart.CartLine("B", false),
                new Cart.CartLine("C", true), new Cart.CartLine("D", false)));
        alternating.removeExpired();
        if (!alternating.lines().equals(List.of(
                new Cart.CartLine("B", false), new Cart.CartLine("D", false)))) {
            throw new AssertionError("alternating lines were not handled");
        }
    }
}
