import java.util.ArrayList;
import java.util.Arrays;

public final class CatalogSearchHiddenTest {
    public static void main(String[] args) {
        var source = new ArrayList<>(Arrays.asList(
                null,
                new CatalogSearch.Product(" ab-1 ", "first"),
                new CatalogSearch.Product("ZZ-1", "other"),
                new CatalogSearch.Product("AB-2", "second")));
        var result = new CatalogSearch().findByPrefix(source, " ab ");
        if (result.size() != 2 || !" ab-1 ".equals(result.get(0).sku())
                || !"AB-2".equals(result.get(1).sku())) {
            throw new AssertionError("trimmed case-insensitive lookup or order is wrong");
        }
        result.clear();
        if (source.size() != 4) throw new AssertionError("result aliases source");
        if (!new CatalogSearch().findByPrefix(null, "AB").isEmpty()
                || !new CatalogSearch().findByPrefix(source, " ").isEmpty()) {
            throw new AssertionError("null/blank input handling is wrong");
        }
        System.out.println("hidden catalog checks passed");
    }
}
