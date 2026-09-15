import java.util.List;

public final class CartPublicTest {
    public static void main(String[] args) {
        Cart cart = new Cart(List.of(
                new Cart.CartLine("A", false),
                new Cart.CartLine("B", true),
                new Cart.CartLine("C", false)));
        cart.removeExpired();
        if (!cart.lines().equals(List.of(
                new Cart.CartLine("A", false), new Cart.CartLine("C", false)))) {
            throw new AssertionError("expired line was not removed while preserving order");
        }
    }
}
