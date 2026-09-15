import java.util.Locale;

public final class CustomerGreetingHiddenTest {
    public static void main(String[] args) {
        if (!"Hello, Ada!".equals(CustomerGreeting.greeting(" Ada "))
                || !"Bonjour, Ada!".equals(CustomerGreeting.greeting(" Ada ", Locale.FRENCH))
                || !"Hallo, Ada!".equals(CustomerGreeting.greeting("Ada", Locale.GERMAN))
                || !"Hello, Ada!".equals(CustomerGreeting.greeting("Ada", null))) {
            throw new AssertionError("compatible or localized greeting is wrong");
        }
        for (String name : new String[] {null, "", " \t "}) {
            try {
                CustomerGreeting.greeting(name, Locale.US);
                throw new AssertionError("invalid name accepted");
            } catch (IllegalArgumentException expected) {
                // expected
            }
        }
        System.out.println("hidden greeting checks passed");
    }
}
