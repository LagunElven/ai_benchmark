public final class VersionedProfile {
    private long version;
    private String name;
    private String email;

    public VersionedProfile(String name, String email) {
        this.name = name; this.email = email;
    }
    public long version() { return version; }
    public String name() { return name; }
    public String email() { return email; }

    public boolean update(long expectedVersion, String newName, String newEmail) {
        if (newName != null) name = newName;
        if (newEmail != null) email = newEmail;
        version++;
        return true;
    }
}
