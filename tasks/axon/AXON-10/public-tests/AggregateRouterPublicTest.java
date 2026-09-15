public final class AggregateRouterPublicTest {
    public static void main(String[] args) {
        var router = new AggregateRouter();
        if (router.dispatch(new AggregateRouter.Command("Order", "o-1", 3)) != 3) {
            throw new AssertionError("aggregate command was not routed");
        }
        System.out.println("public aggregate routing checks passed");
    }
}
