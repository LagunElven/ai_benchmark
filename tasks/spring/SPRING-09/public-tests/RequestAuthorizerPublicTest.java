import java.util.Map;

public final class RequestAuthorizerPublicTest {
    public static void main(String[] args) {
        var request = new RequestAuthorizer.Request("GET", "/orders", Map.of("Authorization", "Bearer t"));
        if (!new RequestAuthorizer().isAllowed(request, "t", "csrf")) {
            throw new AssertionError("authorized GET rejected");
        }
        System.out.println("public security checks passed");
    }
}
