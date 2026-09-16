import java.math.BigDecimal;

public final class AccountStatus {
    public enum Code { ZERO_BALANCE, DELINQUENT, ACTIVE }

    private AccountStatus() {}

    public static Code classify(BigDecimal balance, int daysPastDue) {
        if (balance == null || balance.signum() < 0 || daysPastDue < 0) {
            throw new IllegalArgumentException("invalid account status input");
        }
        if (daysPastDue >= 30) return Code.DELINQUENT;
        if (balance.signum() == 0) return Code.ZERO_BALANCE;
        return Code.ACTIVE;
    }
}
