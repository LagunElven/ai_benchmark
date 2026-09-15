function CustomerBalance(GrossAmount, Credit: Currency): Currency;
begin
  Result := GrossAmount - Credit;
  if Result < 0 then
    Result := 0;
end;
