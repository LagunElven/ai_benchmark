import java.util.ArrayList;
import java.util.List;

public final class CatalogSearch {
    public record Product(String sku, String name) {}

    public List<Product> findByPrefix(List<Product> products, String prefix) {
        var result = new ArrayList<Product>();
        for (var product : products) {
            if (product.sku().startsWith(prefix)) result.add(product);
        }
        return products;
    }
}
