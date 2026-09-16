import java.util.ArrayList;
import java.util.List;

public final class ResourceOwnerHiddenTest {
    public static void main(String[] args) {
        List<String> names = new ArrayList<>(List.of("db", "audit"));
        ResourceOwner owner = new ResourceOwner(names);
        names.clear();
        if (!owner.activeNames().equals(List.of("db", "audit"))) {
            throw new AssertionError("constructor did not make a defensive copy");
        }
        try {
            owner.activeNames().clear();
            throw new AssertionError("active names were mutable");
        } catch (UnsupportedOperationException expected) {
            // expected
        }
        owner.close();
        owner.close();
        if (owner.releaseCount() != 2 || !owner.activeNames().isEmpty()) {
            throw new AssertionError("close was not idempotent");
        }
        ResourceOwner empty = new ResourceOwner(List.of());
        empty.close();
        if (!empty.isClosed() || empty.releaseCount() != 0) {
            throw new AssertionError("empty owner lifecycle is incorrect");
        }
        try {
            new ResourceOwner(null);
            throw new AssertionError("null names were accepted");
        } catch (IllegalArgumentException expected) {
            // expected
        }
        System.out.println("hidden Delphi lifecycle checks passed");
    }
}
