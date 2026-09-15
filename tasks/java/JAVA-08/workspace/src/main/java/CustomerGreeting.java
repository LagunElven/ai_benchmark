import java.util.Locale;

public final class CustomerGreeting {
    private CustomerGreeting() {}

    public static String greeting(String name) {
        return "Hello, " + name + "!";
    }

    public static String greeting(String name, Locale locale) {
        throw new UnsupportedOperationException("new API not implemented");
    }
}
