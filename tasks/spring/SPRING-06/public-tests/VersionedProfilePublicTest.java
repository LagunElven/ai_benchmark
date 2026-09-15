public final class VersionedProfilePublicTest {
    public static void main(String[] args) {
        var profile = new VersionedProfile("Ada", "ada@example.test");
        if (!profile.update(0, "Ada Lovelace", null) || profile.version() != 1
                || !"ada@example.test".equals(profile.email())) {
            throw new AssertionError("versioned update failed");
        }
        System.out.println("public versioned-update checks passed");
    }
}
