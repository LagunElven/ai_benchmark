public final class RegistrationValidatorPublicTest {
    public static void main(String[] args) {
        var validator = new RegistrationValidator();
        if (!validator.validate(new RegistrationValidator.Registration(
                "user@example.test", "tenant-1", 21)).isEmpty()) {
            throw new AssertionError("valid registration rejected");
        }
        if (validator.validate(new RegistrationValidator.Registration(
                "", "tenant-1", 17)).size() != 2) {
            throw new AssertionError("basic validation errors missing");
        }
        System.out.println("public registration checks passed");
    }
}
