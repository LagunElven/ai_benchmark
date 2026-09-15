import java.util.List;

public final class CatalogSearchPublicTest {
    public static void main(String[] args) {
        var products = List.of(new CatalogSearch.Product("AB-1", "A"));
        var result = new CatalogSearch().findByPrefix(products, "ab");
        if (result.size() != 1 || !"AB-1".equals(result.get(0).sku())) {
            throw new AssertionError("prefix lookup failed");
        }
        System.out.println("public catalog checks passed");
    }
}
