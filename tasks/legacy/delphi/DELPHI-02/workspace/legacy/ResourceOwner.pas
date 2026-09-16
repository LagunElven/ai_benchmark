unit ResourceOwner;

interface

uses
  Classes, Contnrs;

type
  TNamedResource = class
  private
    FName: string;
  public
    constructor Create(const AName: string);
    property Name: string read FName;
  end;

  TResourceOwner = class
  private
    FResources: TObjectList;
    FClosed: Boolean;
    FReleaseCount: Integer;
  public
    constructor Create(const Names: array of string);
    destructor Destroy; override;
    procedure Close;
    function ActiveCount: Integer;
    function ReleaseCount: Integer;
    function IsClosed: Boolean;
  end;

implementation

constructor TNamedResource.Create(const AName: string);
begin
  inherited Create;
  FName := AName;
end;

constructor TResourceOwner.Create(const Names: array of string);
var
  I: Integer;
begin
  inherited Create;
  FResources := TObjectList.Create(True);
  FClosed := False;
  FReleaseCount := 0;
  for I := Low(Names) to High(Names) do
    FResources.Add(TNamedResource.Create(Names[I]));
end;

destructor TResourceOwner.Destroy;
begin
  Close;
  FResources.Free;
  inherited Destroy;
end;

procedure TResourceOwner.Close;
begin
  if FClosed then
    Exit;
  FReleaseCount := FReleaseCount + FResources.Count;
  FResources.Clear;
  FClosed := True;
end;

function TResourceOwner.ActiveCount: Integer;
begin
  Result := FResources.Count;
end;

function TResourceOwner.ReleaseCount: Integer;
begin
  Result := FReleaseCount;
end;

function TResourceOwner.IsClosed: Boolean;
begin
  Result := FClosed;
end;

end.
