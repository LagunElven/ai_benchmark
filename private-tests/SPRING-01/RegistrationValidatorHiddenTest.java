public final class RegistrationValidatorHiddenTest {
    public static void main(String[] args) {
        var validator = new RegistrationValidator();
        var errors = validator.validate(null);
        if (errors.size() != 3 || !errors.get(0).startsWith("email")) {
            throw new AssertionError("null request must report all fields in order");
        }
        errors = validator.validate(new RegistrationValidator.Registration(
                " a@@example.test ", "Tenant_1", 18));
        if (errors.size() != 2 || !errors.get(0).startsWith("email")
                || !errors.get(1).startsWith("tenant")) {
            throw new AssertionError("email and tenant constraints are incomplete");
        }
        if (!validator.validate(new RegistrationValidator.Registration(
                " a@example.test ", "tenant-1", 18)).isEmpty()) {
            throw new AssertionError("trimmed boundary values should be accepted");
        }
        System.out.println("hidden registration checks passed");
    }
}
