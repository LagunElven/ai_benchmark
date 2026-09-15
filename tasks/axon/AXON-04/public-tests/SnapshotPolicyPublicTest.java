public final class SnapshotPolicyPublicTest {
    public static void main(String[] args) {
        if (!new SnapshotPolicy().shouldLoad("Order", "Order", 2, 2)) {
            throw new AssertionError("current snapshot rejected");
        }
        System.out.println("public snapshot checks passed");
    }
}
