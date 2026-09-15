import java.util.List;

public final class CustomerRepositoryPublicTest {
    public static void main(String[] args) {
        var customers = List.of(
                new CustomerRepository.Customer("c-1", "EU", true),
                new CustomerRepository.Customer("c-2", "EU", false));
        var result = new CustomerRepository().findActiveByRegion(customers, "eu");
        if (result.size() != 1 || !"c-1".equals(result.get(0).id())) {
            throw new AssertionError("active region filter failed");
        }
        System.out.println("public WLanguage checks passed");
    }
}
