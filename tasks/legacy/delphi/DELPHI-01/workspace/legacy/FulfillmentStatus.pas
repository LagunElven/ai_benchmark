unit FulfillmentStatus;

interface

function StatusForStock(OnHand, Reserved, ReorderPoint: Integer): string;

implementation

uses
  SysUtils;

function StatusForStock(OnHand, Reserved, ReorderPoint: Integer): string;
var
  Available: Integer;
begin
  if (OnHand < 0) or (Reserved < 0) or (ReorderPoint < 0) or
     (Reserved > OnHand) then
    raise Exception.Create('invalid stock values');

  Available := OnHand - Reserved;
  if Available = 0 then
    Result := 'BACKORDER'
  else if Available <= ReorderPoint then
    Result := 'REORDER'
  else
    Result := 'READY';
end;

end.
