public final class ApiErrorMapperHiddenTest {
    public static void main(String[] args) {
        var mapper = new ApiErrorMapper();
        var notFound = mapper.toResponse(new ApiErrorMapper.NotFoundException("secret id"));
        if (notFound.status() != 404 || !"not_found".equals(notFound.code())
                || !"secret id".equals(notFound.message())) {
            throw new AssertionError("not-found mapping is incorrect");
        }
        var unexpected = mapper.toResponse(new IllegalStateException("database password"));
        if (unexpected.status() != 500 || !"internal_error".equals(unexpected.code())
                || !"Internal server error".equals(unexpected.message())) {
            throw new AssertionError("unexpected error leaked details");
        }
        var nullError = mapper.toResponse(null);
        if (nullError.status() != 500 || !"Internal server error".equals(nullError.message())) {
            throw new AssertionError("null error was not mapped generically");
        }
        System.out.println("hidden API error checks passed");
    }
}
