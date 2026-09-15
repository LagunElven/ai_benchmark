public final class AggregateRouterHiddenTest {
    public static void main(String[] args) {
        var router = new AggregateRouter();
        router.dispatch(new AggregateRouter.Command("Order", "o-1", 3));
        if (router.dispatch(new AggregateRouter.Command("Order", "o-1", 2)) != 5
                || router.total("Order", "o-1") != 5) {
            throw new AssertionError("same aggregate total is wrong");
        }
        router.dispatch(new AggregateRouter.Command("Order", "o-2", 7));
        if (router.total("Order", "o-1") != 5 || router.total("Customer", "o-1") != 0) {
            throw new AssertionError("aggregate identity leaked across ids or types");
        }
        for (AggregateRouter.Command invalid : new AggregateRouter.Command[] {
                null, new AggregateRouter.Command("", "x", 1),
                new AggregateRouter.Command("Order", " ", 1),
                new AggregateRouter.Command("Order", "x", 0),
                new AggregateRouter.Command("Unknown", "x", 1)}) {
            try {
                router.dispatch(invalid);
                throw new AssertionError("invalid command accepted");
            } catch (IllegalArgumentException expected) {
                // expected
            }
        }
        System.out.println("hidden aggregate routing checks passed");
    }
}
