public final class ApiErrorMapperPublicTest {
    public static void main(String[] args) {
        var mapper = new ApiErrorMapper();
        var response = mapper.toResponse(new IllegalArgumentException("bad field"));
        if (response.status() != 400 || !"invalid_request".equals(response.code())) {
            throw new AssertionError("bad request was not mapped");
        }
        System.out.println("public API error checks passed");
    }
}
