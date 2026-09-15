public final class ApiErrorMapper {
    public static final class NotFoundException extends RuntimeException {
        public NotFoundException(String message) {
            super(message);
        }
    }

    public record ApiError(int status, String code, String message) {}

    public ApiError toResponse(Throwable error) {
        if (error instanceof NotFoundException) {
            return new ApiError(500, "internal_error", error.getMessage());
        }
        return new ApiError(500, "internal_error", error == null ? "" : error.getMessage());
    }
}
