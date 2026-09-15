import java.util.Locale;

public final class CustomerGreetingPublicTest {
    public static void main(String[] args) {
        if (!"Hello, Ada!".equals(CustomerGreeting.greeting("Ada", Locale.US))) {
            throw new AssertionError("default greeting changed");
        }
        System.out.println("public greeting checks passed");
    }
}
