import java.util.Map;

public final class TransferServicePublicTest {
    public static void main(String[] args) {
        var accounts = new TransferService.Accounts(Map.of("a", 1_000, "b", 0));
        if (!new TransferService().transfer(accounts, "a", "b", 250)
                || accounts.balance("a") != 750 || accounts.balance("b") != 250) {
            throw new AssertionError("ordinary transfer failed");
        }
        System.out.println("public transfer checks passed");
    }
}
