public final class AuditSequence {
    private long next;

    public AuditSequence(long initial) {
        if (initial < 0) throw new IllegalArgumentException("negative initial");
        next = initial;
    }

    public long nextId() {
        long value = next;
        Thread.yield();
        next = value + 1;
        return value;
    }
}
