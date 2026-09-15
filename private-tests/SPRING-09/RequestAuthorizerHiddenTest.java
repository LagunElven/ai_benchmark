import java.util.HashMap;

public final class RequestAuthorizerHiddenTest {
    public static void main(String[] args) {
        var headers = new HashMap<String, String>();
        headers.put("authorization", "Bearer t");
        headers.put("X-CSRF-TOKEN", "csrf");
        var post = new RequestAuthorizer.Request("post", "/orders", headers);
        if (!new RequestAuthorizer().isAllowed(post, "t", "csrf")) {
            throw new AssertionError("case-insensitive POST authorization rejected");
        }
        headers.remove("X-CSRF-TOKEN");
        if (new RequestAuthorizer().isAllowed(post, "t", "csrf")) {
            throw new AssertionError("POST without CSRF accepted");
        }
        var before = new HashMap<>(headers);
        var get = new RequestAuthorizer.Request("HEAD", "/orders", before);
        before.put("Authorization", "Bearer t");
        if (!new RequestAuthorizer().isAllowed(get, "t", "csrf") || !before.equals(get.headers())) {
            throw new AssertionError("HEAD or request immutability failed");
        }
        if (new RequestAuthorizer().isAllowed(null, "t", "csrf")
                || new RequestAuthorizer().isAllowed(get, " ", "csrf")) {
            throw new AssertionError("invalid credentials accepted");
        }
        System.out.println("hidden security checks passed");
    }
}
