public final class AuditSequencePublicTest {
    public static void main(String[] args) {
        var sequence = new AuditSequence(10);
        if (sequence.nextId() != 10 || sequence.nextId() != 11) {
            throw new AssertionError("sequential ids are incorrect");
        }
        System.out.println("public sequence checks passed");
    }
}
