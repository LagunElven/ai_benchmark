import java.util.ArrayList;
import java.util.Arrays;

public final class CustomerRepositoryHiddenTest {
    public static void main(String[] args) {
        var source = new ArrayList<>(Arrays.asList(
                null,
                new CustomerRepository.Customer("c-1", " EU ", true),
                new CustomerRepository.Customer("c-2", "EU", false),
                new CustomerRepository.Customer("c-3", "EU", true)));
        var result = new CustomerRepository().findActiveByRegion(source, " eu ");
        if (result.size() != 2 || !"c-1".equals(result.get(0).id())
                || !"c-3".equals(result.get(1).id())) {
            throw new AssertionError("trimmed case-insensitive HFSQL filter failed");
        }
        result.clear();
        if (source.size() != 4) throw new AssertionError("result aliases source");
        if (!new CustomerRepository().findActiveByRegion(null, "EU").isEmpty()
                || !new CustomerRepository().findActiveByRegion(source, " ").isEmpty()) {
            throw new AssertionError("null/blank region handling failed");
        }
        System.out.println("hidden WLanguage checks passed");
    }
}
