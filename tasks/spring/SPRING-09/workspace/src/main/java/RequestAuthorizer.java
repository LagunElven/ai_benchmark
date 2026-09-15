import java.util.Map;

public final class RequestAuthorizer {
    public record Request(String method, String path, Map<String, String> headers) {}

    public boolean isAllowed(Request request, String bearerToken, String csrfToken) {
        if (request == null || bearerToken == null || bearerToken.isBlank()) return false;
        String authorization = request.headers().get("Authorization");
        if (!(("Bearer " + bearerToken).equals(authorization))) return false;
        return true;
    }
}
