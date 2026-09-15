import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.HashSet;

public final class TransferService {
    public static final class Accounts {
        private final Map<String, Integer> balances = new HashMap<>();
        private final Set<String> rejectedCredits = new HashSet<>();

        public Accounts(Map<String, Integer> initial) { balances.putAll(initial); }
        public void rejectCreditsFor(String account) { rejectedCredits.add(account); }
        public int balance(String account) { return balances.getOrDefault(account, 0); }
        private boolean debit(String account, int cents) {
            int current = balance(account);
            if (!balances.containsKey(account) || current < cents) return false;
            balances.put(account, current - cents);
            return true;
        }
        private boolean credit(String account, int cents) {
            if (!balances.containsKey(account) || rejectedCredits.contains(account)) return false;
            balances.put(account, balances.get(account) + cents);
            return true;
        }
        private void restore(String account, int cents) { balances.put(account, cents); }
    }

    public boolean transfer(Accounts accounts, String from, String to, int cents) {
        if (accounts == null || from == null || to == null || from.equals(to) || cents <= 0) {
            return false;
        }
        if (!accounts.debit(from, cents)) return false;
        if (accounts.credit(to, cents)) return true;
        accounts.restore(from, accounts.balance(from) + cents);
        return false;
    }
}
