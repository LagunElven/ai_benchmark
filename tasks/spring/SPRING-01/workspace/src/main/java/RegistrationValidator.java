import java.util.ArrayList;
import java.util.List;

public final class RegistrationValidator {
    public record Registration(String email, String tenant, Integer age) {}

    public List<String> validate(Registration request) {
        var errors = new ArrayList<String>();
        if (request == null) {
            return List.of("email is required", "tenant is required", "age is required");
        }
        if (request.email() == null || request.email().trim().isEmpty()
                || request.email().indexOf('@') < 0) {
            errors.add("email is invalid");
        }
        if (request.tenant() == null || request.tenant().trim().isEmpty()) {
            errors.add("tenant is required");
        }
        if (request.age() == null || request.age() < 18) {
            errors.add("age must be at least 18");
        }
        return errors;
    }
}
