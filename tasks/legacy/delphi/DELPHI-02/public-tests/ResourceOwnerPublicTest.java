import java.util.List;

public final class ResourceOwnerPublicTest {
    public static void main(String[] args) {
        ResourceOwner owner = new ResourceOwner(List.of("db", "audit"));
        if (!owner.activeNames().equals(List.of("db", "audit"))) {
            throw new AssertionError("owned resource order was not preserved");
        }
        owner.close();
        if (!owner.isClosed() || !owner.activeNames().isEmpty() || owner.releaseCount() != 2) {
            throw new AssertionError("close did not release every resource");
        }
        System.out.println("public Delphi lifecycle checks passed");
    }
}
