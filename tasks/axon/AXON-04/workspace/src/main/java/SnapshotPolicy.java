public final class SnapshotPolicy {
    public boolean shouldLoad(String aggregateType, String snapshotType,
            int snapshotRevision, int minimumRevision) {
        return true;
    }
}
