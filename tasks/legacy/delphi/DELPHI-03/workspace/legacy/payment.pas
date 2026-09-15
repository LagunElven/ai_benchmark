{ Synthetic Delphi fixture; syntax is illustrative until a native compiler is available. }
function TotalCents(AmountCents: Integer; Method: String): Integer;
begin
  if (UpperCase(Method) = 'CARD') and (AmountCents >= 10000) then
    TotalCents := AmountCents + (AmountCents div 50)
  else
    TotalCents := AmountCents;
end;
