public final class SnapshotPolicyHiddenTest {
    public static void main(String[] args) {
        var policy = new SnapshotPolicy();
        if (policy.shouldLoad("Order", "Order", 1, 2)) {
            throw new AssertionError("obsolete matching snapshot accepted");
        }
        if (!policy.shouldLoad("Order", "Invoice", 1, 2)
                || !policy.shouldLoad("Order", "Order", 2, 2)) {
            throw new AssertionError("unrelated or boundary snapshot rejected");
        }
        if (policy.shouldLoad(null, "Order", 1, 2)
                || policy.shouldLoad("Order", "Order", -1, 0)) {
            throw new AssertionError("invalid snapshot metadata accepted");
        }
        System.out.println("hidden snapshot checks passed");
    }
}
